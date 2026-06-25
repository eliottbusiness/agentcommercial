# SKILL: Intent Signal Detection
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Détecter automatiquement les signaux d'intention d'achat à travers le web et les réseaux sociaux. **Objectif**: >= 40% des prospects avec au moins 1 signal détecté, taux de confiance >= 0.7.

---

### SOURCES DE SIGNAUX

#### 1. Twitter/X (via Agent Reach)
**Outil**: `twitter search` (twitter-cli via cookie)
**Coût**: $0 | **Limite**: Usage raisonnable (risque ban si abus)

**Signaux détectables**:
```
Type: hiring_spree
Pattern: "recrute .* développeur|hiring .* engineer|on recherche .* tech|postes ouverts"
Impact: 8 | Confiance: 0.85

Type: pain_point_mention
Pattern: "galère .* infra|problème .* scaling|bug .* production|lent .* API|crash .* serveur"
Impact: 9 | Confiance: 0.80

Type: budget_mention
Pattern: "budget .* 2026|investissement .* tech|nouveau .* outil|cherche .* solution"
Impact: 8 | Confiance: 0.75

Type: decision_maker_change
Pattern: "nouveau .* CTO|rejoint .* tech lead|promu .* directeur technique|changement .* DSI"
Impact: 7 | Confiance: 0.80

Type: expansion
Pattern: "nouveau .* bureau|ouverture .* agence|expansion .* international|recrutement .* Paris|Lyon|Marseille"
Impact: 7 | Confiance: 0.85

Type: product_launch
Pattern: "lancement .* produit|nouvelle .* version|release .* majeure|beta .* ouverte"
Impact: 6 | Confiance: 0.80
```

**Workflow**:
```
1. Pour chaque prospect actif:
   a. Construire requête: "from:company_twitter OR @company_twitter {{pattern}}"
   b. Exécuter via agent-reach twitter search
   c. Parser résultats
   d. Pour chaque match:
      - Extraire: texte, date, URL, auteur
      - Calculer confiance (source vérifiée? date récente? clarté?)
      - Insérer dans intent_signals
   e. Recalculer intent_score
```

---

#### 2. Reddit (via Agent Reach)
**Outil**: `reddit search` (OpenCLI via cookie)
**Coût**: $0 | **Limite**: Usage raisonnable

**Signaux détectables**:
```
Type: pain_point_mention
Subreddits: r/france, r/entrepreneur, r/webdev, r/sysadmin, r/startups
Pattern: "recommandation .* hébergeur|quelle .* solution .* cloud|besoin .* automatiser|problème .* scaling"
Impact: 9 | Confiance: 0.75

Type: budget_mention
Pattern: "budget .* développement|coût .* serveur|devis .* prestation|tarif .* SaaS"
Impact: 8 | Confiance: 0.70

Type: competitor_switch
Pattern: "déçu .* {{competitor_name}}|cherche .* alternative .* {{competitor_name}}|migration .* depuis .* {{competitor_name}}"
Impact: 10 | Confiance: 0.80
```

---

#### 3. Job Boards (via Exa Search)
**Outil**: `exa_search`
**Coût**: $0 (150/jour) | **Limite**: 150 calls/jour

**Signaux détectables**:
```
Type: hiring_spree
Query: "site:linkedin.com/jobs "{{company_name}}" "développeur" OR "engineer" OR "devops""
Impact: 8 | Confiance: 0.90

Type: tech_stack_change
Query: "site:linkedin.com/jobs "{{company_name}}" "Kubernetes" OR "Docker" OR "AWS" OR "React""
Impact: 7 | Confiance: 0.85

Type: senior_hiring
Query: "site:linkedin.com/jobs "{{company_name}}" "lead" OR "architect" OR "principal" OR "staff""
Impact: 9 | Confiance: 0.85
```

---

#### 4. GitHub (via Agent Reach)
**Outil**: `gh repo view`, `gh search repos`
**Coût**: $0 | **Limite**: 5000 req/heure (authentifié)

**Signaux détectables**:
```
Type: tech_stack_change
Pattern: "new repo .* microservices|migration .* kubernetes|refactor .* architecture|adoption .* {{technology}}"
Impact: 7 | Confiance: 0.75

Type: open_source_activity
Pattern: "new contributors .* +5|issues .* scaling|discussions .* performance"
Impact: 6 | Confiance: 0.70
```

---

#### 5. SIRENE / INPI (via DataGouv MCP)
**Outil**: `search_datasets`, `query_resource_data`
**Coût**: $0 | **Limite**: 30 req/min

**Signaux détectables**:
```
Type: capital_increase
Query: "capital social" changement récent
Impact: 10 | Confiance: 0.95

Type: director_change
Query: changement mandataire social récent
Impact: 7 | Confiance: 0.90

Type: new_establishment
Query: nouvel établissement ouvert
Impact: 6 | Confiance: 0.85
```

---

#### 6. Exa Company Intelligence
**Outil**: `exa_company_search`, `exa_contents`
**Coût**: $0 (150/jour) | **Limite**: 150 calls/jour

**Signaux détectables**:
```
Type: funding_announcement
Query: "{{company_name}} funding OR raise OR series OR levée de fonds"
Impact: 10 | Confiance: 0.90

Type: press_coverage
Query: "{{company_name}} expansion OR new office OR partnership OR acquisition"
Impact: 7 | Confiance: 0.80

Type: product_launch
Query: "{{company_name}} launch OR new product OR beta OR release"
Impact: 6 | Confiance: 0.80
```

---

### ALGORITHME DE CONFIDENCE SCORING

```python
def calculate_confidence(signal):
    base_confidence = 0.5

    # Source reliability
    source_weights = {
        'sirene_api': 0.95,
        'exa_company': 0.90,
        'job_boards': 0.85,
        'twitter': 0.80,
        'github': 0.75,
        'reddit': 0.70,
        'website_crawl': 0.80
    }

    # Date freshness
    days_old = (now - signal.date).days
    if days_old <= 1:
        freshness = 0.10
    elif days_old <= 7:
        freshness = 0.05
    elif days_old <= 30:
        freshness = 0.00
    else:
        freshness = -0.20

    # Clarity of signal
    clarity = signal.explicitness * 0.10  # 0.0-1.0

    # Verification
    if signal.verified_by_second_source:
        verification = 0.10
    else:
        verification = 0.00

    confidence = base_confidence + source_weights[signal.source] + freshness + clarity + verification
    return min(1.0, max(0.0, confidence))
```

---

### MÉTRIQUES SIGNAUX

- **Coverage**: >= 40% des prospects avec >= 1 signal
- **Precision**: >= 80% des signaux détectés sont réels (vérifié manuellement sur échantillon)
- **Recall**: >= 70% des signaux réels sont détectés
- **Freshness**: >= 60% des signaux ont < 7 jours
- **Diversity**: >= 3 types de signaux différents dans la base
- **Processing time**: < 4h entre découverte brute et insertion en base
