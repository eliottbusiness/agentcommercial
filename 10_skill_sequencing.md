# SKILL: Outreach Sequencing
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Orchestrer des séquences d'outreach multi-canal avec timing optimal pour maximiser les réponses sans harceler. **Règle d'or**: Max 5 touches sur 21 jours, puis nurture passif.

---

### ARCHITECTURE DES SÉQUENCES

#### Séquence A: SUPER HOT (Priority >= 85)
**Durée**: 14 jours | **Touches**: 5 | **Canaux**: Email → LinkedIn → Email → Email → LinkedIn

```
Jour 0 (T+0h):  Email 1 - Hyper-personnalisé, signal principal
Jour 2 (T+48h): LinkedIn - Connection request + note value
Jour 4 (T+96h): Email 2 - Follow-up avec nouvelle valeur (si pas de réponse)
Jour 7 (T+168h): Email 3 - Case study similaire (si pas de réponse)
Jour 14 (T+336h): LinkedIn - Soft touch, contenu pertinent (si pas de réponse)
→ Après J14: Passage en nurture (newsletter mensuelle)
```

**Conditions d'arrêt**:
- Réponse positive → Sortie séquence, entrée process RDV
- Réponse négative → Sortie séquence, tag "not_now", nurture 90 jours
- "Pas intéressé" → Sortie séquence, tag "lost", analyse raison

---

#### Séquence B: HOT (Priority 70-84)
**Durée**: 21 jours | **Touches**: 4 | **Canaux**: Email → Email → LinkedIn → Email

```
Jour 0 (T+0h):  Email 1 - Personnalisé, contexte sectoriel
Jour 3 (T+72h): Email 2 - Follow-up avec insight additionnel
Jour 7 (T+168h): LinkedIn - Connection + message court
Jour 14 (T+336h): Email 3 - Contenu value (case study, rapport)
→ Après J14: Nurture (contenu mensuel)
```

---

#### Séquence C: WARM (Priority 41-69)
**Durée**: 30 jours | **Touches**: 3 | **Canaux**: Email → Email → LinkedIn

```
Jour 0 (T+0h):  Email 1 - Éducatif, insight sectoriel
Jour 7 (T+168h): Email 2 - Contenu value (article, rapport)
Jour 14 (T+336h): LinkedIn - Connection + partage contenu
→ Après J14: Nurture (newsletter)
```

---

#### Séquence D: NURTURE (Priority < 41)
**Durée**: Continue | **Touches**: 1/mois | **Canaux**: Newsletter

```
Mensuel: Newsletter sectorielle personnalisée
- Article pertinent pour le secteur du prospect
- Case study d'entreprise similaire
- Invitation événement (webinar, meetup)
- Réactivation si signal d'intention détecté
```

---

### LOGIQUE DE DÉCISION PAR ÉTAPE

```
Après chaque envoi:
  SI réponse_positive:
    → Arrêter séquence
    → Créer interaction "positive_response"
    → Proposer RDV via Cal.com
    → Status: "responded"

  SI réponse_négative:
    → Arrêter séquence
    → Créer interaction "negative_response"
    → Analyser raison (budget, timing, besoin, concurrent)
    → Tag prospect selon raison
    → Status: "lost" OU "nurture"

  SI pas_de_réponse:
    → Attendre délai prochaine étape
    → Vérifier pas d'email récent (< 7 jours)
    → Vérifier prospect toujours hot (score >= seuil)
    → Passer à étape suivante

  SI email_bounced:
    → Arrêter séquence
    → Flag prospect: email_invalid
    → Chercher nouvel email (re-enrichment)
    → Si nouvel email trouvé: recommencer séquence
    → Sinon: status "unreachable"

  SI meeting_booked:
    → Arrêter séquence
    → Créer interaction "meeting_booked"
    → Envoyer préparation RDV (24h avant)
    → Status: "meeting_booked"
```

---

### RÈGLES DE TIMING

**Timing optimal basé sur données**:
- **Mardi-Jeudi**: Meilleurs jours pour emails B2B
- **10h-11h**: Meilleur créneau matin
- **14h-15h**: Meilleur créneau après-midi
- **Éviter**: Lundi matin, Vendredi après-midi, jours fériés

**Délais entre touches**:
- Email → Email: minimum 48h
- Email → LinkedIn: minimum 24h
- LinkedIn → Email: minimum 72h
- Dernière touche → Nurture: minimum 14 jours

---

### GESTION DES RÉPONSES

#### Réponse Positive
```
1. Détecter sentiment positif (NLP ou keywords: "intéressé", "disponible", "parlons-en", "RDV")
2. Extraire préférences: horaires, format (visio/physique), participants
3. Générer lien Cal.com avec créneaux adaptés
4. Envoyer confirmation avec brief préparation
5. Créer tâche préparation RDV (24h avant)
6. Mettre à jour status: "meeting_booked"
```

#### Réponse Négative
```
1. Détecter sentiment négatif (keywords: "pas intéressé", "pas le moment", "pas de budget")
2. Catégoriser raison:
   - "pas le moment" → Tag: "timing", Nurture 90j
   - "pas de budget" → Tag: "budget", Nurture 180j
   - "pas de besoin" → Tag: "no_fit", Archive
   - "déjà prestataire" → Tag: "competitor", Nurture 365j
   - "trop cher" → Tag: "pricing", Nurture 90j
3. Réponse polie courte: "Merci pour votre retour, je vous recontacterai dans X mois"
4. Mettre à jour status selon tag
```

#### Réponse Neutre/Question
```
1. Détecter question ou demande info
2. Générer réponse personnalisée avec réponse précise
3. Proposer RDV si question complexe
4. Ne pas repartir en séquence automatique
5. Attendre réponse humaine ou prochain signal
```

---

### MÉTRIQUES SÉQUENCES

- **Reply rate par séquence**: 
  - Super Hot: >= 40%
  - Hot: >= 25%
  - Warm: >= 15%

- **Meeting rate par séquence**:
  - Super Hot: >= 30%
  - Hot: >= 15%
  - Warm: >= 5%

- **Unsubscribe rate**: < 2%
- **Bounce rate**: < 5%
- **Séquences actives max**: 50 simultanées (pour maintenir qualité)
- **Temps moyen entre découverte et premier contact**: < 24h
