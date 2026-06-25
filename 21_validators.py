#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de validation et auto-verification pour l'Agent Commercial Autonome.
Implemente la boucle d'auto-verification avant chaque action critique.

Principes:
1. Verifier la coherence des donnees avant insertion
2. Verifier la qualite des emails avant envoi
3. Verifier la non-duplication
4. Verifier les rate limits
5. Verifier les dependances workflows
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('AgentCommercial.Validators')


@dataclass
class ValidationResult:
    is_valid: bool
    check_name: str
    message: str
    severity: str
    action: Optional[str] = None
    data: Optional[Dict] = None


class DataIntegrityValidator:
    """Validateur d'integrite des donnees prospects."""

    @staticmethod
    def validate_siret(siret: str) -> ValidationResult:
        if not siret or len(siret) != 14:
            return ValidationResult(
                is_valid=False,
                check_name='siret_format',
                message=f'SIRET invalide: {siret} (doit avoir 14 chiffres)',
                severity='error',
                action='re_enrich_via_sirene_api'
            )

        if not siret.isdigit():
            return ValidationResult(
                is_valid=False,
                check_name='siret_numeric',
                message=f'SIRET non numerique: {siret}',
                severity='error',
                action='flag_for_manual_review'
            )

        def luhn_check(num: str) -> bool:
            total = 0
            for i, digit in enumerate(reversed(num)):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
            return total % 10 == 0

        if not luhn_check(siret):
            return ValidationResult(
                is_valid=False,
                check_name='siret_luhn',
                message=f'Cle Luhn invalide pour SIRET: {siret}',
                severity='warning',
                action='flag_for_manual_review'
            )

        return ValidationResult(
            is_valid=True,
            check_name='siret_valid',
            message=f'SIRET valide: {siret}',
            severity='info'
        )

    @staticmethod
    def validate_siren(siren: str) -> ValidationResult:
        if not siren or len(siren) != 9:
            return ValidationResult(
                is_valid=False,
                check_name='siren_format',
                message=f'SIREN invalide: {siren}',
                severity='error',
                action='re_enrich_via_sirene_api'
            )

        if not siren.isdigit():
            return ValidationResult(
                is_valid=False,
                check_name='siren_numeric',
                message=f'SIREN non numerique: {siren}',
                severity='error',
                action='flag_for_manual_review'
            )

        return ValidationResult(
            is_valid=True,
            check_name='siren_valid',
            message=f'SIREN valide: {siren}',
            severity='info'
        )

    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        if not email:
            return ValidationResult(
                is_valid=False,
                check_name='email_empty',
                message='Email vide',
                severity='warning',
                action='search_alternative_email'
            )

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return ValidationResult(
                is_valid=False,
                check_name='email_format',
                message=f'Format email invalide: {email}',
                severity='warning',
                action='search_alternative_email'
            )

        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return ValidationResult(
                is_valid=False,
                check_name='email_disposable',
                message=f'Domaine jetable detecte: {domain}',
                severity='error',
                action='discard_prospect'
            )

        return ValidationResult(
            is_valid=True,
            check_name='email_valid',
            message=f'Email valide: {email}',
            severity='info'
        )

    @staticmethod
    def validate_scores(intent_score: int, fit_score: int, priority_score: int) -> List[ValidationResult]:
        results = []
        for score_name, score in [('intent_score', intent_score), ('fit_score', fit_score), ('priority_score', priority_score)]:
            if score is None:
                results.append(ValidationResult(
                    is_valid=False,
                    check_name=f'{score_name}_null',
                    message=f'{score_name} est null',
                    severity='warning',
                    action='recalculate_score'
                ))
            elif score < 0 or score > 100:
                results.append(ValidationResult(
                    is_valid=False,
                    check_name=f'{score_name}_out_of_range',
                    message=f'{score_name} hors bornes: {score} (doit etre 0-100)',
                    severity='error',
                    action='recalculate_score'
                ))
            else:
                results.append(ValidationResult(
                    is_valid=True,
                    check_name=f'{score_name}_valid',
                    message=f'{score_name} valide: {score}',
                    severity='info'
                ))
        return results

    @staticmethod
    def validate_status(status: str) -> ValidationResult:
        valid_statuses = [
            'discovered', 'enriched', 'qualified', 'hot_lead',
            'contacted', 'responded', 'meeting_booked', 'proposal_sent',
            'negotiation', 'won', 'lost', 'nurture'
        ]

        if status not in valid_statuses:
            return ValidationResult(
                is_valid=False,
                check_name='status_invalid',
                message=f'Statut invalide: {status}',
                severity='error',
                action='reset_to_discovered'
            )

        return ValidationResult(
            is_valid=True,
            check_name='status_valid',
            message=f'Statut valide: {status}',
            severity='info'
        )


class DeduplicationValidator:
    """Validateur de deduplication."""

    @staticmethod
    def check_duplicate_siret(siret: str, existing_sirets: List[str]) -> ValidationResult:
        if siret in existing_sirets:
            return ValidationResult(
                is_valid=False,
                check_name='duplicate_siret',
                message=f'SIRET deja existant: {siret}',
                severity='error',
                action='merge_duplicates_or_flag'
            )
        return ValidationResult(
            is_valid=True,
            check_name='siret_unique',
            message=f'SIRET unique: {siret}',
            severity='info'
        )

    @staticmethod
    def check_similar_company(company_name: str, city: str, existing_companies: List[Dict]) -> ValidationResult:
        similar = []
        for existing in existing_companies:
            name_similarity = DeduplicationValidator._name_similarity(
                company_name.lower(), 
                existing['company_name'].lower()
            )
            if name_similarity > 0.8 and existing['city'] == city:
                similar.append(existing)

        if similar:
            return ValidationResult(
                is_valid=False,
                check_name='similar_company',
                message=f'Entreprise similaire detectee: {similar[0]["company_name"]} a {city}',
                severity='warning',
                action='manual_review_similar'
            )

        return ValidationResult(
            is_valid=True,
            check_name='company_unique',
            message='Entreprise unique',
            severity='info'
        )

    @staticmethod
    def _name_similarity(name1: str, name2: str) -> float:
        set1 = set(name1.split())
        set2 = set(name2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0


class EmailQualityValidator:
    """Validateur de qualite des emails d'outreach."""

    SPAM_KEYWORDS = [
        'gratuit', 'promotion', 'offre limitee', 'urgent', 'gagner',
        'cliquez ici', 'action immediate', 'ne manquez pas', 'derniere chance',
        '100% gratuit', 'sans engagement', 'satisfait ou rembourse'
    ]

    @staticmethod
    def validate_email_quality(email_content: str) -> List[ValidationResult]:
        results = []

        word_count = len(email_content.split())
        if word_count < 100:
            results.append(ValidationResult(
                is_valid=False,
                check_name='email_too_short',
                message=f'Email trop court: {word_count} mots (min: 100)',
                severity='warning',
                action='add_more_personalization'
            ))
        elif word_count > 300:
            results.append(ValidationResult(
                is_valid=False,
                check_name='email_too_long',
                message=f'Email trop long: {word_count} mots (max: 300)',
                severity='warning',
                action='condense_email'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='email_length_ok',
                message=f'Longueur OK: {word_count} mots',
                severity='info'
            ))

        link_count = email_content.count('http')
        if link_count > 2:
            results.append(ValidationResult(
                is_valid=False,
                check_name='too_many_links',
                message=f'Trop de liens: {link_count} (max: 2)',
                severity='error',
                action='remove_excess_links'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='links_ok',
                message=f'Liens OK: {link_count}',
                severity='info'
            ))

        exclamation_count = email_content.count('!')
        if exclamation_count > 1:
            results.append(ValidationResult(
                is_valid=False,
                check_name='too_many_exclamations',
                message=f'Trop de points d exclamation: {exclamation_count} (max: 1)',
                severity='warning',
                action='remove_excess_exclamations'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='exclamations_ok',
                message='Points d exclamation OK',
                severity='info'
            ))

        uppercase_ratio = sum(1 for c in email_content if c.isupper()) / max(len(email_content), 1)
        if uppercase_ratio > 0.05:
            results.append(ValidationResult(
                is_valid=False,
                check_name='too_many_uppercase',
                message=f'Trop de majuscules: {uppercase_ratio:.1%} (max: 5%)',
                severity='warning',
                action='reduce_uppercase'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='uppercase_ok',
                message='Majuscules OK',
                severity='info'
            ))

        spam_found = [kw for kw in EmailQualityValidator.SPAM_KEYWORDS if kw.lower() in email_content.lower()]
        if spam_found:
            results.append(ValidationResult(
                is_valid=False,
                check_name='spam_keywords',
                message=f'Mots spam detectes: {spam_found}',
                severity='error',
                action='rewrite_to_avoid_spam'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='no_spam_keywords',
                message='Aucun mot spam detecte',
                severity='info'
            ))

        template_markers = ['Cher client', 'Nous sommes', 'Notre entreprise', 'Cordialement,', 'Votre equipe']
        template_score = sum(1 for marker in template_markers if marker.lower() in email_content.lower())
        if template_score >= 3:
            results.append(ValidationResult(
                is_valid=False,
                check_name='template_detected',
                message=f'Template evident detecte ({template_score} markers)',
                severity='error',
                action='regenerate_with_more_research'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='no_template',
                message='Pas de template evident',
                severity='info'
            ))

        errors = [r for r in results if not r.is_valid and r.severity == 'error']
        warnings = [r for r in results if not r.is_valid and r.severity == 'warning']

        if errors:
            results.append(ValidationResult(
                is_valid=False,
                check_name='overall_quality',
                message=f'Email invalide: {len(errors)} erreurs, {len(warnings)} warnings',
                severity='critical',
                action='regenerate_email'
            ))
        elif warnings:
            results.append(ValidationResult(
                is_valid=True,
                check_name='overall_quality',
                message=f'Email acceptable avec {len(warnings)} warnings',
                severity='warning'
            ))
        else:
            results.append(ValidationResult(
                is_valid=True,
                check_name='overall_quality',
                message='Email de haute qualite',
                severity='info'
            ))

        return results

    @staticmethod
    def calculate_spam_score(email_content: str) -> float:
        score = 0.0
        spam_words = sum(1 for kw in EmailQualityValidator.SPAM_KEYWORDS if kw.lower() in email_content.lower())
        score += min(0.3, spam_words * 0.05)
        uppercase_ratio = sum(1 for c in email_content if c.isupper()) / max(len(email_content), 1)
        score += min(0.2, uppercase_ratio * 2)
        exclamation_ratio = email_content.count('!') / max(len(email_content.split('.')), 1)
        score += min(0.2, exclamation_ratio * 0.5)
        link_ratio = email_content.count('http') / max(len(email_content.split()), 1)
        score += min(0.2, link_ratio * 5)
        template_score = sum(1 for marker in ['Cher client', 'Nous sommes', 'Cordialement,'] 
                           if marker.lower() in email_content.lower())
        score += min(0.1, template_score * 0.03)
        return min(1.0, score)

    @staticmethod
    def calculate_personalization_score(email_content: str, prospect_data: Dict) -> float:
        score = 0.0
        checks = 0

        if prospect_data.get('company_name', '').lower() in email_content.lower():
            score += 0.2
        checks += 1

        if prospect_data.get('decision_maker_name', '').lower() in email_content.lower():
            score += 0.2
        checks += 1

        if prospect_data.get('city', '').lower() in email_content.lower():
            score += 0.1
        checks += 1

        if prospect_data.get('naf_label', '').lower() in email_content.lower():
            score += 0.1
        checks += 1

        signals = prospect_data.get('intent_signals', {})
        if signals and any(str(v).lower() in email_content.lower() for v in signals.values() if isinstance(v, str)):
            score += 0.2
        checks += 1

        tech_stack = prospect_data.get('tech_stack', [])
        if tech_stack and any(tech.lower() in email_content.lower() for tech in tech_stack):
            score += 0.1
        checks += 1

        word_count = len(email_content.split())
        if 100 <= word_count <= 250:
            score += 0.1
        checks += 1

        return score / max(checks, 1) if checks > 0 else 0.0


class SequenceCoherenceValidator:
    """Validateur de coherence des sequences d'outreach."""

    @staticmethod
    def validate_sequence_step(prospect_id: str, step_number: int, 
                               previous_steps: List[Dict]) -> ValidationResult:
        completed_steps = [s for s in previous_steps if s.get('status') == 'completed']
        if len(completed_steps) < step_number - 1:
            return ValidationResult(
                is_valid=False,
                check_name='previous_steps_incomplete',
                message=f'Etape {step_number} impossible: {len(completed_steps)}/{step_number-1} etapes precedentes completees',
                severity='error',
                action='wait_or_skip'
            )

        recent_emails = [s for s in previous_steps 
                        if s.get('channel') == 'email' 
                        and s.get('sent_at') 
                        and (datetime.now() - datetime.fromisoformat(s['sent_at'])).days < 7]
        if recent_emails:
            return ValidationResult(
                is_valid=False,
                check_name='recent_email_exists',
                message=f'Email recent detecte (il y a {(datetime.now() - datetime.fromisoformat(recent_emails[0]["sent_at"])).days} jours)',
                severity='warning',
                action='wait_before_next_email'
            )

        return ValidationResult(
            is_valid=True,
            check_name='sequence_step_valid',
            message=f'Etape {step_number} peut etre envoyee',
            severity='info'
        )

    @staticmethod
    def validate_no_duplicate_email(prospect_id: str, email_subject: str,
                                    previous_emails: List[Dict]) -> ValidationResult:
        subject_hash = hashlib.md5(email_subject.lower().encode()).hexdigest()

        for prev in previous_emails:
            prev_hash = hashlib.md5(prev.get('subject', '').lower().encode()).hexdigest()
            if prev_hash == subject_hash:
                return ValidationResult(
                    is_valid=False,
                    check_name='duplicate_email_subject',
                    message='Email avec sujet identique deja envoye',
                    severity='error',
                    action='abort_and_log'
                )

        return ValidationResult(
            is_valid=True,
            check_name='email_unique',
            message='Email unique',
            severity='info'
        )


class RateLimitValidator:
    """Validateur de rate limits."""

    LIMITS = {
        'exa': {'daily': 150, 'description': 'Exa MCP free tier'},
        'sirene': {'per_minute': 30, 'description': 'INSEE SIRENE API'},
        'overpass': {'daily': 10000, 'description': 'Overpass API'},
        'twitter': {'per_hour': 100, 'description': 'Twitter via Agent Reach'},
        'reddit': {'per_hour': 50, 'description': 'Reddit via Agent Reach'},
        'github': {'per_hour': 5000, 'description': 'GitHub API'},
        'cal_com': {'per_minute': 60, 'description': 'Cal.com API'},
    }

    def __init__(self):
        self.usage = {
            service: {'count': 0, 'last_reset': datetime.now()}
            for service in self.LIMITS
        }

    def check_limit(self, service: str) -> ValidationResult:
        if service not in self.LIMITS:
            return ValidationResult(
                is_valid=True,
                check_name='unknown_service',
                message=f'Service inconnu: {service}',
                severity='warning'
            )

        limit = self.LIMITS[service]
        usage = self.usage[service]

        now = datetime.now()
        if 'daily' in limit and (now - usage['last_reset']).days >= 1:
            usage['count'] = 0
            usage['last_reset'] = now
        elif 'per_minute' in limit and (now - usage['last_reset']).seconds >= 60:
            usage['count'] = 0
            usage['last_reset'] = now
        elif 'per_hour' in limit and (now - usage['last_reset']).seconds >= 3600:
            usage['count'] = 0
            usage['last_reset'] = now

        limit_value = limit.get('daily') or limit.get('per_minute') or limit.get('per_hour')
        if usage['count'] >= limit_value:
            return ValidationResult(
                is_valid=False,
                check_name='rate_limit_exceeded',
                message=f'Rate limit depasse pour {service}: {usage["count"]}/{limit_value}',
                severity='error',
                action='throttle_and_retry_later'
            )

        return ValidationResult(
            is_valid=True,
            check_name='rate_limit_ok',
            message=f'Rate limit OK pour {service}: {usage["count"]}/{limit_value}',
            severity='info'
        )

    def increment(self, service: str):
        if service in self.usage:
            self.usage[service]['count'] += 1


async def validate_before_action(action_type: str, data: Dict, 
                                  validators: List[Any]) -> Tuple[bool, List[ValidationResult]]:
    all_results = []

    for validator in validators:
        if action_type == 'insert_prospect':
            if hasattr(validator, 'validate_siret'):
                all_results.append(validator.validate_siret(data.get('siret')))
            if hasattr(validator, 'validate_siren'):
                all_results.append(validator.validate_siren(data.get('siren')))
            if hasattr(validator, 'validate_email'):
                all_results.append(validator.validate_email(data.get('contact_email')))
            if hasattr(validator, 'validate_scores'):
                all_results.extend(validator.validate_scores(
                    data.get('intent_score'), 
                    data.get('fit_score'), 
                    data.get('priority_score')
                ))
            if hasattr(validator, 'validate_status'):
                all_results.append(validator.validate_status(data.get('status')))

        elif action_type == 'send_email':
            if hasattr(validator, 'validate_email_quality'):
                all_results.extend(validator.validate_email_quality(data.get('content')))
            if hasattr(validator, 'calculate_spam_score'):
                spam_score = validator.calculate_spam_score(data.get('content'))
                if spam_score > 0.3:
                    all_results.append(ValidationResult(
                        is_valid=False,
                        check_name='spam_score_too_high',
                        message=f'Score spam trop eleve: {spam_score:.2f} (max: 0.3)',
                        severity='error',
                        action='rewrite_to_avoid_spam'
                    ))
            if hasattr(validator, 'calculate_personalization_score'):
                perso_score = validator.calculate_personalization_score(
                    data.get('content'), 
                    data.get('prospect', {})
                )
                if perso_score < 0.7:
                    all_results.append(ValidationResult(
                        is_valid=False,
                        check_name='personalization_too_low',
                        message=f'Score personnalisation trop faible: {perso_score:.2f} (min: 0.7)',
                        severity='error',
                        action='regenerate_with_more_research'
                    ))

    errors = [r for r in all_results if not r.is_valid and r.severity in ('error', 'critical')]
    is_valid = len(errors) == 0

    return is_valid, all_results


if __name__ == '__main__':
    validator = DataIntegrityValidator()

    print("Test SIRET:")
    print(validator.validate_siret("12345678901234"))

    print("\nTest Email:")
    print(validator.validate_email("test@example.com"))

    print("\nTest Email Quality:")
    email = """
    Bonjour Jean,

    J'ai vu que TechCorp recrute 5 developpeurs sur LinkedIn - c'est impressionnant !

    En parcourant votre site, j'ai remarque votre migration vers Kubernetes. 
    Nous avons aide DataFlow (35 pers., SaaS) a passer de "deploiements manuels" 
    a "livraisons quotidiennes" en 6 semaines.

    Je vous propose un echange de 20 minutes:
    https://cal.com/rdv

    A bientot,
    Marie
    """
    print(EmailQualityValidator.validate_email_quality(email))
