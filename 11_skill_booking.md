# SKILL: Meeting Booking
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Automatiser la prise de rendez-vous via Cal.com avec qualification préalable et préparation optimale. **Objectif**: Taux de show >= 80%, taux de conversion meeting → proposal >= 60%.

---

### INTÉGRATION CAL.COM

#### Configuration API
```yaml
API: Cal.com v2
Auth: Bearer ${CAL_COM_API_KEY}
Base URL: https://api.cal.com/v2
Rate Limit: 60 req/min, 1000 req/jour
Cost: Free tier 25 bookings/mois, $0.99 au-delà
```

#### Event Types Utilisés
1. **discovery_call** (30 min): Premier échange qualification
2. **demo_call** (45 min): Démonstration personnalisée post-discovery
3. **follow_up** (15 min): Suivi rapide ou questions

---

### WORKFLOW DE PRISE DE RDV

#### Étape 1: Détection Intent Booking
```
Trigger: prospect.status = "hot_lead" OR prospect.status = "responded"
Condition: prospect.intent_score >= 70 AND prospect.priority_score >= 70
Vérification: Pas de RDV existant dans les 7 jours
```

#### Étape 2: Sélection Event Type
```
SI prospect.status = "hot_lead" ET jamais contacté:
  → Event type: "discovery_call" (30 min)

SI prospect.status = "responded" ET meeting déjà eu:
  → Event type: "demo_call" (45 min)

SI prospect.status = "proposal_sent":
  → Event type: "follow_up" (15 min)
```

#### Étape 3: Génération Lien Personnalisé
```
1. Construire URL Cal.com:
   https://cal.com/${CAL_USERNAME}/${event_type}?name=${prospect.decision_maker_name}&email=${prospect.decision_maker_email}&guests=${prospect.contact_email}

2. Paramètres pré-remplis:
   - name: Nom décideur
   - email: Email décideur
   - guests: Emails additionnels si connus
   - notes: Contexte brief pour le prospect

3. UTM tracking:
   - utm_source: agent_autonome
   - utm_medium: email
   - utm_campaign: ${sequence_name}
   - utm_content: ${prospect.id}
```

#### Étape 4: Email de Proposition RDV
```
Objet: Votre appel découverte - {{prospect.company_name}}

Bonjour {{prospect.decision_maker_name}},

Merci pour votre intérêt. Comme évoqué, je vous propose un échange de 
{{duration}} minutes pour explorer ensemble:

• Vos objectifs actuels sur {{prospect.pain_point}}
• Comment nous avons aidé {{similar_company}} à {{similar_result}}
• Une première estimation de faisabilité pour {{prospect.company_name}}

Voici mon calendrier avec des créneaux adaptés à votre fuseau horaire:
👉 {{cal_link}}

Je reste disponible si aucun créneau ne convient.

{{agent_name}}
```

#### Étape 5: Suivi Post-Booking (Automatique via Webhook)

**Webhook Cal.com → Supabase Edge Function**:
```
Endpoint: ${SUPABASE_EDGE_FUNCTION_URL}/cal-webhook
Secret: ${CAL_WEBHOOK_SECRET}

Events écoutés:
- booking_created
- booking_rescheduled  
- booking_cancelled
- booking_completed
- booking_no_show
```

**Actions par event**:

**booking_created**:
```
1. Créer interaction: type="meeting_booked", channel="cal_com"
2. Mettre à jour prospect: status="meeting_booked", next_action_date=booking_date
3. Planifier email préparation (24h avant RDV)
4. Planifier email rappel (1h avant RDV)
5. Générer brief préparation (contexte prospect, questions, objections)
```

**booking_rescheduled**:
```
1. Mettre à jour interaction: type="meeting_rescheduled"
2. Mettre à jour prospect: next_action_date=new_date
3. Replanifier emails préparation/rappel
```

**booking_cancelled**:
```
1. Créer interaction: type="meeting_cancelled", channel="cal_com"
2. Mettre à jour prospect: status="nurture"
3. Envoyer email: "Pas de souci, je vous recontacterai dans X semaines"
4. Planifier re-engagement dans 30-60 jours
```

**booking_completed**:
```
1. Créer interaction: type="meeting_completed", channel="cal_com"
2. Analyser sentiment (si notes de réunion disponibles)
3. SI sentiment positif:
   - Status: "proposal_sent" (si démo) ou "negotiation"
   - Proposer prochain RDV (démo ou follow-up)
4. SI sentiment neutre:
   - Status: "nurture"
   - Envoyer contenu value additionnel
5. SI sentiment négatif:
   - Status: "lost"
   - Analyser raison, taguer
```

**booking_no_show**:
```
1. Créer interaction: type="meeting_no_show", channel="cal_com"
2. Envoyer email: "Désolé de vous avoir manqué, voici un nouveau lien"
3. Proposer 2 créneaux spécifiques (pas de lien ouvert)
4. SI 2 no-shows consécutifs: status="unreachable", nurture passif
```

---

### PRÉPARATION DES RDV

#### Brief Pré-RDV (Généré auto 24h avant)
```
PROSPECT: {{prospect.company_name}}
RDV: {{date}} à {{heure}} avec {{decision_maker_name}}

CONTEXTE:
- Secteur: {{naf_label}}
- Taille: {{employee_count_band}} salariés
- CA estimé: {{revenue_estimate}}€
- Tech stack: {{tech_stack}}
- Signaux d'intention: {{intent_signals_summary}}

HISTORIQUE INTERACTIONS:
{{last_5_interactions}}

QUESTIONS À POSER:
1. "Quel est votre principal défi actuel sur {{pain_point}}?"
2. "Quelle est votre timeline pour résoudre ce problème?"
3. "Qui d'autre est impliqué dans cette décision?"
4. "Avez-vous déjà exploré des solutions? Quels ont été les blocages?"
5. "Quel budget avez-vous alloué pour ce projet?"

OBJECTIONS ANTICIPÉES:
{{likely_objections_based_on_signals}}

SOCIAL PROOF PRÊT:
- Case study similaire: {{similar_company}}
- Résultat: {{similar_result}}
- Témoignage: {{testimonial_quote}}

PROCHAINES ÉTAPES À PROPOSER:
{{next_steps_based_on_meeting_type}}
```

---

### MÉTRIQUES BOOKING

- **Show rate**: >= 80% (personnes qui se présentent au RDV)
- **Conversion meeting → proposal**: >= 60%
- **Conversion meeting → won**: >= 30%
- **Temps moyen entre booking et meeting**: < 7 jours
- **Taux de reschedule**: < 20%
- **Taux de no-show**: < 15%
- **Satisfaction post-meeting**: >= 4.0/5.0
