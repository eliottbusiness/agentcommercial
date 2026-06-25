# 🤖 Agent Commercial Autonome
## Version 1.0 | Stack 100% Gratuite | Objectif: 1 Prospect = 1 Client

---

## 📋 Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT COMMERCIAL AUTONOME                     │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Discovery   │  │  Enrichment  │  │   Scoring    │         │
│  │   Engine     │  │   Engine     │  │   Engine     │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                    │
│                    ┌──────┴──────┐                            │
│                    │  Supabase   │  ← CRM Central              │
│                    │  PostgreSQL │                             │
│                    └──────┬──────┘                            │
│                           │                                    │
│         ┌─────────────────┼─────────────────┐                │
│         │                 │                 │                │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐          │
│  │  Outreach   │  │   Booking   │  │  Feedback   │          │
│  │   Engine    │  │   Engine    │  │   Loop      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              VALIDATORS (Auto-Verification)              │  │
│  │  • Data Integrity  • Deduplication  • Email Quality       │  │
│  │  • Sequence Coherence  • Rate Limits  • Spam Detection   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Stack Technique (100% Gratuite)

| Outil | Rôle | Coût | Limites Free |
|-------|------|------|-------------|
| **DataGouv MCP** | Données entreprises françaises (SIRENE) | $0 | 30 req/min |
| **Exa MCP** | Recherche sémantique web, entreprises | $0 | 150/jour (unauth) |
| **Overpass API** | Entreprises physiques par zone géo | $0 | ~10 000/jour |
| **Agent Reach** | Scraping web, Twitter, Reddit, GitHub | $0 | Illimité (raisonnable) |
| **Google MCP Toolbox** | Accès Supabase PostgreSQL | $0 | Self-hosted |
| **Supabase** | Base CRM PostgreSQL | $0 | 500MB, 50K MAU |
| **Cal.com** | Prise de rendez-vous | $0 | 25 bookings/mois |
| **Composio** | Orchestration (optionnel) | $0 | Usage généreux |

---

## 📁 Structure du Projet

```
agent-commercial-autonome/
│
├── config/
│   ├── 01_mcp_servers.json          # Configuration MCP (DataGouv, Exa, Toolbox, Agent Reach, Overpass)
│   ├── 02_tools.yaml                # Google MCP Toolbox (SQL tools pour Supabase)
│   ├── 03_supabase_schema.sql       # Schéma complet CRM (prospects, interactions, signals, sequences)
│   ├── 04_cal_com_config.yaml       # Configuration Cal.com (event types, webhooks, templates)
│   └── 05_agent_config.yaml         # Configuration agent (ICP, scoring, sequences, validation)
│
├── skills/
│   ├── prospection/
│   │   ├── 06_discovery.md          # Skill découverte prospects (SIRENE, Overpass, Exa)
│   │   ├── 07_enrichment.md         # Skill enrichissement profond (web, tech stack, décideurs)
│   │   └── 08_scoring.md            # Skill scoring intention (formules, seuils, algorithmes)
│   │
│   ├── outreach/
│   │   ├── 09_personalization.md    # Skill personnalisation emails (frameworks, anti-spam)
│   │   ├── 10_sequencing.md         # Skill séquences multi-canal (timing, gestion réponses)
│   │   └── 11_booking.md            # Skill prise de RDV (Cal.com, webhooks, briefs)
│   │
│   └── analysis/
│       ├── 12_intent_signals.md     # Skill signaux d'intention (sources, patterns, confidence)
│       └── (market_research.md)      # Recherche marché (optionnel)
│
├── workflows/
│   ├── 13_workflow_01_signal_detection.yaml      # Toutes les 4h
│   ├── 14_workflow_02_prospect_discovery.yaml      # 6h00 quotidien
│   ├── 15_workflow_03_deep_enrichment.yaml         # Toutes les 2h
│   ├── 16_workflow_04_intent_scoring.yaml          # Toutes les heures
│   ├── 17_workflow_05_personalized_outreach.yaml  # Toutes les 2h
│   ├── 18_workflow_06_meeting_booking.yaml         # Event-driven + horaire
│   └── 19_workflow_07_feedback_loop.yaml           # 8h00 quotidien
│
├── src/
│   ├── 20_orchestrator.py           # Orchestrateur principal (7 workflows, scheduling)
│   ├── 21_validators.py             # Moteur d'auto-vérification (5 validateurs)
│   ├── enrichment_engine.py         # (TODO) Moteur d'enrichissement
│   └── scoring_engine.py            # (TODO) Moteur de scoring
│
└── README.md                        # Ce fichier
```

---

## 🎯 Philosophie: 1 Prospect = 1 Client

### Principe Fondamental
L'agent ne cherche pas à contacter 1000 prospects. Il cherche à **identifier 10 prospects parfaitement qualifiés** et à les convertir un par un.

### Méthodologie
1. **Signal-first**: Chaque prospect commence par un signal d'intention détecté (pas de cold outreach aveugle)
2. **Deep research**: 10-15 min de recherche par prospect super hot (site web + LinkedIn + Twitter + GitHub + presse)
3. **Hyper-personnalisation**: Chaque email est unique, basé sur des éléments spécifiques du prospect
4. **Value alignment**: La proposition de valeur est calibrée sur le pain point identifié
5. **Social proof pertinent**: Case study d'une entreprise similaire (même secteur, même taille, même problème)

### Seuils de Qualité
| Score | Catégorie | Action | Objectif Conversion |
|-------|-----------|--------|-------------------|
| 85-100 | Super Hot | Outreach immédiat, RDV sous 48h | 80% → Meeting |
| 70-84 | Hot | Outreach personnalisé, proposition valeur | 50% → Meeting |
| 41-69 | Warm | Outreach éducatif, contenu value | 20% → Meeting |
| 0-40 | Cold | Nurture uniquement | 5% → Meeting |

---

## 🔧 Installation & Configuration

### 1. Supabase (Base de données)
```bash
# Créer un projet sur supabase.com (free tier)
# Exécuter le schéma SQL
psql $SUPABASE_URL -f config/03_supabase_schema.sql
```

### 2. Variables d'environnement
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_PASSWORD="your-db-password"
export CAL_COM_API_KEY="your-cal-api-key"
export CAL_USERNAME="your-cal-username"
```

### 3. Google MCP Toolbox
```bash
# Installer le serveur MCP Toolbox
npx -y @toolbox-sdk/server --prebuilt=postgres --stdio
# Configurer les variables d'environnement pour la connexion Supabase
```

### 4. Agent Reach
```bash
pip install agent-reach
agent-reach install
# Configurer les cookies pour Twitter/Reddit si nécessaire
```

### 5. Orchestrateur
```bash
pip install -r requirements.txt  # asyncio, yaml, requests, etc.
python src/20_orchestrator.py
```

---

## 🔄 Workflows Automatiques

### Workflow 01: Signal Detection (Toutes les 4h)
- **Sources**: Twitter, Reddit, Job Boards, GitHub, SIRENE, Exa
- **Action**: Détecte signaux d'intention, insère dans `intent_signals`
- **Output**: Nouveaux hot leads identifiés

### Workflow 02: Prospect Discovery (6h00 quotidien)
- **Sources**: SIRENE API, Overpass API, Exa Search
- **Quota**: Max 50 nouveaux prospects/jour
- **Filtre**: ICP strict (secteur, taille, localisation)

### Workflow 03: Deep Enrichment (Toutes les 2h)
- **Actions**: Scraping web, recherche décideurs, détection tech stack
- **Objectif**: 100% enrichis sous 24h, complétude >= 80%

### Workflow 04: Intent Scoring (Toutes les heures)
- **Formule**: Intent(40%) + Recency(25%) + Diversity(20%) + Engagement(15%)
- **Fit**: Sector(25%) + Size(20%) + Location(15%) + Tech(20%) + Pain(20%)
- **Priority**: Intent(60%) + Fit(40%)

### Workflow 05: Personalized Outreach (Toutes les 2h)
- **Quota**: Max 10 emails/jour
- **Validation**: Anti-spam + personnalisation >= 70% + gate humain super hot
- **Séquences**: 5 touches max sur 14-21 jours

### Workflow 06: Meeting Booking (Event-driven + horaire)
- **Trigger**: Réponse positive détectée
- **Action**: Génération lien Cal.com, envoi proposition, préparation brief
- **Suivi**: Rappels 24h et 1h avant RDV

### Workflow 07: Feedback Loop (8h00 quotidien)
- **Analyse**: Funnel conversion, patterns succès/échec, performance séquences
- **Auto-ajustement**: ICP weights, sequence timing, source focus
- **Rapport**: KPIs quotidiens + recommandations

---

## 🛡 Auto-Vérification (Boucle de Cohérence)

### Validateurs Implémentés

#### 1. DataIntegrityValidator
- SIRET: 14 chiffres + clé Luhn
- SIREN: 9 chiffres
- Email: format valide, pas de domaine jetable
- Scores: bornes 0-100
- Statut: dans liste autorisée

#### 2. DeduplicationValidator
- SIRET unique
- Similarité nom + ville (Jaccard > 80%)
- Flag `is_duplicated` + `duplicate_of`

#### 3. EmailQualityValidator
- Longueur: 100-300 mots
- Liens: max 2
- Exclamations: max 1
- Majuscules: < 5%
- Mots spam: blacklist
- Template detection: < 3 markers
- Score spam: < 0.3
- Personnalisation: >= 70%

#### 4. SequenceCoherenceValidator
- Étapes précédentes complétées
- Pas d'email récent (< 7 jours)
- Pas de sujet dupliqué

#### 5. RateLimitValidator
- Exa: 150/jour
- SIRENE: 30/min
- Overpass: 10 000/jour
- Twitter: 100/heure
- Reddit: 50/heure
- GitHub: 5000/heure
- Cal.com: 60/min

---

## 📊 KPIs & Objectifs

### Objectifs Principaux
| KPI | Target | Fréquence |
|-----|--------|-----------|
| Conversion globale (discovered → won) | >= 30% | Mensuel |
| Taux de réponse email | >= 25% (Hot), >= 15% (Warm) | Hebdomadaire |
| Taux de show RDV | >= 80% | Hebdomadaire |
| Meeting → Proposal | >= 60% | Mensuel |
| Proposal → Won | >= 50% | Mensuel |

### Objectifs Qualité
| KPI | Target | Fréquence |
|-----|--------|-----------|
| Complétude enrichment | >= 80% | Quotidien |
| Précision signaux | >= 80% | Mensuel |
| Score spam email | < 0.3 | Par email |
| Personnalisation | >= 70% | Par email |
| Temps discovery → contact | < 24h | Quotidien |

---

## 🚀 Roadmap

### Phase 1: MVP (Actuel)
- [x] Configuration MCP servers
- [x] Schéma Supabase
- [x] Workflows YAML
- [x] Orchestrateur Python
- [x] Validateurs auto-vérification
- [ ] Implémentation engines (enrichment, scoring)
- [ ] Tests end-to-end

### Phase 2: Optimisation
- [ ] Machine learning pour scoring
- [ ] NLP avancé pour détection signaux
- [ ] A/B testing séquences
- [ ] Intégration LinkedIn API (si gratuit)

### Phase 3: Scale
- [ ] Multi-langue (EN, DE, ES)
- [ ] Expansion sources (AngelList, Crunchbase)
- [ ] Dashboard analytics temps réel

---

## 📄 Licence

MIT License - Stack 100% open source et gratuite.

## 🤝 Contribution

Les contributions sont les bienvenues ! Priorité aux améliorations de:
1. Précision des signaux d'intention
2. Qualité de personnalisation des emails
3. Taux de conversion meeting → won

---

**Construit avec ❤️ et 0€ de dépenses.**
