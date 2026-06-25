# SKILL: Intent Scoring Engine
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Calculer un score d'intention précis (0-100) pour chaque prospect basé sur des signaux comportementaux et contextuels réels. **Objectif**: Score >= 85 = prospect "super hot" prêt pour outreach immédiat.

---

### ARCHITECTURE DU SCORING

#### Formule Composite
```
INTENT_SCORE = (Signals_Strength * 0.40) + (Recency * 0.25) + (Signal_Diversity * 0.20) + (Engagement * 0.15)

FIT_SCORE = (Sector_Match * 0.25) + (Size_Match * 0.20) + (Location_Match * 0.15) + (Tech_Match * 0.20) + (Pain_Match * 0.20)

PRIORITY_SCORE = (INTENT_SCORE * 0.60) + (FIT_SCORE * 0.40)
```

---

### 1. SIGNALS STRENGTH (40%)

**Définition**: Somme pondérée des impacts des signaux détectés, normalisée.

**Algorithme**:
```python
def calculate_signals_strength(signals):
    total_impact = 0
    max_possible = 0

    for signal in signals:
        # Impact brut du signal (1-10)
        impact = signal.impact_score

        # Pondération par confiance (0.0-1.0)
        confidence = signal.confidence_score

        # Décroissance temporelle (half-life = 7 jours)
        days_old = (now - signal.discovered_at).days
        recency_factor = 0.5 ** (days_old / 7)

        weighted_impact = impact * confidence * recency_factor
        total_impact += weighted_impact
        max_possible += 10  # Impact max par signal

    # Normaliser sur 0-100
    if max_possible == 0:
        return 0
    return min(100, (total_impact / max_possible) * 100)
```

**Exemple**:
- Signal 1: Levée fonds 2M€ (impact=10, conf=0.95, 2 jours) → 10 * 0.95 * 0.82 = 7.79
- Signal 2: Recrutement 3 devs (impact=8, conf=0.85, 5 jours) → 8 * 0.85 * 0.61 = 4.15
- Signal 3: Plainte scaling (impact=9, conf=0.80, 1 jour) → 9 * 0.80 * 0.91 = 6.55
- Total: 18.49 / 30 = 61.6 → **Score Signals: 62**

---

### 2. RECENCY (25%)

**Définition**: Quand le dernier signal a été détecté. Plus c'est récent, plus le prospect est "chaud".

**Algorithme**:
```python
def calculate_recency(last_signal_date):
    if not last_signal_date:
        return 0

    days_since = (now - last_signal_date).days

    # Fonction de décroissance exponentielle
    # 0 jours = 100, 7 jours = 50, 30 jours = 10, 90 jours = 0
    if days_since <= 0:
        return 100
    elif days_since <= 7:
        return 100 - (days_since * 7.14)  # Linéaire 100→50
    elif days_since <= 30:
        return 50 - ((days_since - 7) * 1.74)  # Linéaire 50→10
    elif days_since <= 90:
        return 10 - ((days_since - 30) * 0.17)  # Linéaire 10→0
    else:
        return 0
```

**Exemple**:
- Dernier signal: hier → **Score Recency: 93**
- Dernier signal: il y a 5 jours → **Score Recency: 64**
- Dernier signal: il y a 15 jours → **Score Recency: 36**

---

### 3. SIGNAL DIVERSITY (20%)

**Définition**: Combien de types de signaux différents sont détectés. Un prospect avec 3 types de signaux est plus chaud qu'un avec 3 signaux du même type.

**Algorithme**:
```python
def calculate_diversity(signals):
    unique_types = set(s.type for s in signals)
    total_possible_types = 10  # hiring, funding, pain, expansion, tech_change, budget, decision_change, product_launch, competitor_switch, intent_explicit

    ratio = len(unique_types) / total_possible_types

    # Bonus pour combinaisons puissantes
    bonus = 0
    powerful_combos = [
        {'funding', 'hiring'},           # Levée + recrutement = expansion confirmée
        {'pain', 'budget'},              # Besoin + budget = achat imminent
        {'hiring', 'tech_change'},       # Recrutement + nouvelle tech = transformation
        {'funding', 'expansion'},        # Levée + expansion = croissance rapide
        {'decision_change', 'budget'},   # Nouveau décideur + budget = fenêtre d'opportunité
    ]

    for combo in powerful_combos:
        if combo.issubset(unique_types):
            bonus += 10

    base_score = ratio * 100
    return min(100, base_score + bonus)
```

**Exemple**:
- Signaux: funding, hiring, pain → 3 types + combo funding+hiring → **Score Diversity: 40**
- Signaux: pain, budget, decision_change → 3 types + combo pain+budget + combo decision+budget → **Score Diversity: 60**

---

### 4. ENGAGEMENT (15%)

**Définition**: Niveau d'engagement du prospect avec notre contenu/communications (si déjà contacté).

**Algorithme**:
```python
def calculate_engagement(prospect_id):
    interactions = get_interactions(prospect_id, last_30_days)

    score = 0

    # Email ouvert: +10
    opens = count(interactions, type='email_opened')
    score += min(30, opens * 10)

    # Email répondu: +25
    replies = count(interactions, type='email_replied')
    score += min(50, replies * 25)

    # Clic lien: +15
    clicks = count(interactions, type='link_clicked')
    score += min(30, clicks * 15)

    # Visite site: +10
    visits = count(interactions, type='website_visit')
    score += min(20, visits * 10)

    # RDV pris: +50
    meetings = count(interactions, type='meeting_booked')
    score += min(50, meetings * 50)

    return min(100, score)
```

**Exemple**:
- 2 emails ouverts (+20) + 1 réponse (+25) + 1 clic (+15) = **Score Engagement: 60**
- 1 email ouvert (+10) + 1 visite site (+10) = **Score Engagement: 20**

---

### 5. FIT SCORING (0-100)

#### Sector Match (25%)
```python
def sector_match(naf_code):
    target_nafs = ['62.01Z', '62.02A', '62.03Z', '63.11Z', '63.12Z', '58.29Z', '61.10Z', '71.12Z']
    related_nafs = ['70.10Z', '71.11Z', '62.09Z', '63.99Z']

    if naf_code in target_nafs:
        return 100
    elif naf_code in related_nafs:
        return 70
    else:
        return 30
```

#### Size Match (20%)
```python
def size_match(employee_count):
    ideal_min, ideal_max = 20, 100

    if employee_count is None:
        return 50  # Inconnu = neutre

    if ideal_min <= employee_count <= ideal_max:
        return 100
    elif employee_count < ideal_min:
        # Pénalité progressive sous l'idéal
        return max(0, 100 - (ideal_min - employee_count) * 5)
    else:
        # Pénalité progressive au-dessus
        return max(0, 100 - (employee_count - ideal_max) * 0.5)
```

#### Location Match (15%)
```python
def location_match(city, region):
    priority_regions = ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d'Azur']
    priority_cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux', 'Nantes']

    if city in priority_cities:
        return 100
    elif region in priority_regions:
        return 85
    elif city in france_cities:
        return 70
    else:
        return 40
```

#### Tech Match (20%)
```python
def tech_match(detected_stack):
    target_tech = ['React', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes', 'PostgreSQL']

    if not detected_stack:
        return 50

    matches = sum(1 for tech in detected_stack if tech in target_tech)
    return min(100, (matches / len(target_tech)) * 100 + 20)
```

#### Pain Match (20%)
```python
def pain_match(detected_pains):
    target_pains = ['scaling', 'digital_transformation', 'automation', 'data_pipeline', 'dette_technique', 'recrutement_tech']

    if not detected_pains:
        return 30

    matches = sum(1 for pain in detected_pains if pain in target_pains)
    return min(100, (matches / len(target_pains)) * 100 + 10)
```

---

### SEUILS D'ACTION

| Score | Catégorie | Action |
|-------|-----------|--------|
| 0-40 | Cold | Nurture uniquement, pas d'outreach actif |
| 41-69 | Warm | Outreach éducatif, contenu value, pas de vente directe |
| 70-84 | Hot | Outreach personnalisé, proposition valeur, proposition RDV |
| 85-100 | Super Hot | Outreach immédiat, priorité max, RDV sous 48h |

**Règle critique**: Un prospect Super Hot sans réponse sous 24h perd 10 points de recency.

---

### MÉTRIQUES SCORING

- **Précision**: >= 80% des prospects score >= 85 convertissent en meeting
- **Rappel**: >= 70% des prospects qui convertissent avaient score >= 70
- **Faux positifs**: < 15% (score >= 85 mais pas de meeting)
- **Faux négatifs**: < 10% (score < 70 mais convertissent)
- **Temps de calcul**: < 2s par prospect
