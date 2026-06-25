# SKILL: Outreach Personalization
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Créer des messages d'outreach hyper-personnalisés basés sur les signaux d'intention réels du prospect. **Règle d'or**: Chaque email doit être unique et impossible à confondre avec un template générique.

---

### PRINCIPES DE PERSONNALISATION

1. **Signal-first**: Le message commence TOUJOURS par le signal d'intention détecté
2. **Context-aware**: Référence des éléments spécifiques du prospect (projet, actualité, tech stack)
3. **Value-prop alignée**: La proposition de valeur est calibrée sur le pain point identifié
4. **Social proof pertinent**: Case study d'un client similaire (même secteur, même taille, même problème)
5. **CTA unique**: Un seul appel à l'action clair et contextuel

---

### FRAMEWORK DE PERSONNALISATION

#### Niveau 1: Super Hot (Score >= 85)
**Recherche requise**: Site web + LinkedIn + Twitter + GitHub + Presse + Job boards
**Temps de préparation**: 10-15 min par email
**Longueur**: 150-250 mots

**Structure**:
```
1. Hook signal (1-2 phrases)
   "J'ai vu que {{company_name}} vient de lever {{funding_amount}} - félicitations ! 
    C'est exactement le moment où l'infrastructure technique devient critique."

2. Contexte spécifique (2-3 phrases)
   "En parcourant votre site, j'ai remarqué que vous recrutez {{job_count}} développeurs 
    {{job_specialty}}. C'est un signe fort d'expansion technique."

3. Pain point identifié (1-2 phrases)
   "Cependant, avec cette croissance rapide, {{pain_point}} devient un risque majeur 
    pour votre time-to-market."

4. Value proposition alignée (2-3 phrases)
   "Nous avons aidé {{similar_company}} ({{similar_size}} personnes, secteur {{similar_sector}}) 
    à résoudre exactement ce problème en {{timeframe}}. Résultat: {{metric}}."

5. CTA contextuel (1 phrase)
   "Je vous propose un échange de 20 minutes cette semaine pour explorer comment 
    nous pourrions vous aider à {{objective}}. Voici mon calendrier: {{cal_link}}"
```

**Exemple réel**:
```
Objet: {{company_name}} - Votre recrutement tech + levée récente

Bonjour {{decision_maker_name}},

J'ai vu que {{company_name}} vient de lever 2.5M€ (bravo !) et recrute 4 développeurs 
backend senior sur Welcome to the Jungle. C'est exactement le profil d'entreprise 
que nous accompagnons.

En parcourant votre repo GitHub public, j'ai remarqué votre migration récente vers 
Kubernetes - une excellente décision, mais qui demande une expertise DevOps que 
vous semblez encore structurer (votre offre SRE est encore ouverte).

Nous avons aidé DataFlow (35 personnes, SaaS B2B, levée de 3M€) à passer de 
"déploiements manuels stressants" à "livraisons quotidiennes sans friction" en 6 semaines. 
Leur CTO m'a dit: "On a gagné 15h/semaine d'ingénierie."

Je vous propose un échange de 20 minutes pour voir si nous pouvons vous aider à 
accélérer sans sacrifier la qualité. Mon calendrier: {{cal_link}}

{{agent_name}}
```

---

#### Niveau 2: Hot (Score 70-84)
**Recherche requise**: Site web + LinkedIn + Twitter
**Temps de préparation**: 5-8 min par email
**Longueur**: 120-200 mots

**Structure**:
```
1. Hook contextuel (1 phrase)
   "{{company_name}} est en pleine {{growth_signal}} - c'est impressionnant."

2. Observation sectorielle (1-2 phrases)
   "Dans le secteur {{sector}}, nous voyons souvent que {{common_challenge}} 
    devient un goulot d'étranglement à cette étape."

3. Social proof sectoriel (2 phrases)
   "Nous avons accompagné {{similar_company}} ({{similar_size}} pers., {{sector}}) 
    à surmonter ce défi. Résultat: {{metric}}."

4. CTA (1 phrase)
   "Intéressé par un échange de 20 minutes? {{cal_link}}"
```

---

#### Niveau 3: Warm (Score 41-69)
**Recherche requise**: Site web
**Temps de préparation**: 3-5 min par email
**Longueur**: 100-150 mots

**Structure**:
```
1. Observation (1 phrase)
   "J'ai découvert {{company_name}} en recherchant des entreprises {{sector}} 
    innovantes en {{region}}."

2. Insight sectoriel (1-2 phrases)
   "Un rapport récent de {{source}} montre que {{trend}} est la priorité #1 
    des {{sector}} en 2026."

3. Offre value (1 phrase)
   "J'ai préparé une analyse rapide de comment {{company_name}} pourrait 
    capitaliser sur cette tendance."

4. CTA soft (1 phrase)
   "Ça vous intéresse? {{cal_link}}"
```

---

### RÈGLES ANTI-SPAM

Avant d'envoyer, VÉRIFIER que l'email ne contient PAS:
- [ ] Plus de 2 liens externes
- [ ] Mot "gratuit" ou "promotion"
- [ ] Majuscules excessives
- [ ] Plus de 1 point d'exclamation
- [ ] Template évident ("Cher client", "Nous sommes...")
- [ ] Pièce jointe non sollicitée
- [ ] Demande de référence/recommandation dès le 1er contact
- [ ] Longueur > 300 mots
- [ ] Plus de 3 paragraphes
- [ ] CTA multiple ("Répondez-moi ET prenez RDV ET visitez notre site")

**Score spam target**: < 0.3 (sur échelle 0-1)

---

### TEMPLATES DE SUJET

| Contexte | Sujet |
|----------|-------|
| Levée fonds | "{{company_name}} - Félicitations pour la levée + une question rapide" |
| Recrutement massif | "{{company_name}} - Vos {{n}} recrutements tech et l'infrastructure" |
| Pain point tech | "{{company_name}} - J'ai vu votre discussion sur {{pain}} sur Twitter" |
| Changement CTO | "{{company_name}} - Transition technique + bonnes pratiques" |
| Expansion | "{{company_name}} - Votre nouvel bureau à {{city}} et la scalabilité" |
| Sectoriel | "{{company_name}} - Tendance {{sector}} 2026 et opportunité" |
| Warm | "{{company_name}} - Question rapide sur votre stack technique" |

---

### MÉTRIQUES PERSONNALISATION

- **Unicité**: 100% des emails doivent être uniques (vérifié via hash)
- **Reply rate target**: >= 25% (Hot), >= 15% (Warm)
- **Open rate target**: >= 60%
- **Spam score**: < 0.3
- **Temps de génération**: < 30s par email
