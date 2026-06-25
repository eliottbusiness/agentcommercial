# SKILL: Deep Enrichment
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Transformer un prospect "découvert" en prospect "enrichi" avec données actionnables.
**Objectif**: 100% des prospects enrichis sous 24h, taux de complétude >= 80%.

---

### PIPELINE D'ENRICHISSEMENT

#### Phase 1: Enrichissement Base (SIRENE + DataGouv)
**Outils**: DataGouv MCP, SIRENE API
**Coût**: $0

```
INPUT: SIREN ou SIRET
OUTPUT: Données structurées entreprise

1. Appeler SIRENE API (via DataGouv MCP):
   - Tool: query_resource_data sur dataset Sirene
   - Paramètres: siren=$siren

2. Extraire:
   - Raison sociale complète
   - Forme juridique détaillée
   - Capital social
   - Date immatriculation
   - Tranche effectif mise à jour
   - NAF/APE code + libellé
   - Adresse complète (numéro, rue, CP, ville, pays)
   - SIRET siège + établissements secondaires

3. Appeler INPI RNE (via DataGouv MCP):
   - Tool: search_dataservices pour "RNE"
   - Extraire: mandataires sociaux, statuts, comptes annuels

4. Mettre à jour Supabase:
   - Tool: enrich_prospect_data (Google Toolbox)
   - Champs: company_name, legal_form, naf_code, naf_label, 
             address, city, postal_code, employee_count_band, 
             creation_date, revenue_estimate
```

#### Phase 2: Enrichissement Digital (Site Web + SEO)
**Outils**: Agent Reach (Jina Reader), Exa Search
**Coût**: $0 (Jina Reader gratuit, Exa 150/jour)

```
INPUT: Site web découvert ou recherché
OUTPUT: Tech stack, signaux d'intention, décideurs

1. Découvrir site web:
   a) Si site web connu: Jina Reader direct
      `curl https://r.jina.ai/$website_url`

   b) Si site web inconnu: Exa Search
      `exa_search: "company_name official website"`

2. Scraper site web (Jina Reader):
   - Page d'accueil: description activité, produits, services
   - Page équipe: noms, titres, photos décideurs
   - Page careers: postes ouverts (signal croissance)
   - Page blog: sujets tech, stratégie
   - Page contact: email, téléphone, adresse

3. Analyser tech stack:
   - Détecter: CMS (WordPress, Webflow, etc.)
   - Détecter: frameworks (React, Vue, Angular)
   - Détecter: analytics (Google Analytics, Mixpanel)
   - Détecter: chatbot (Intercom, Crisp, etc.)
   - Détecter: infrastructure (Cloudflare, AWS, etc.)

4. Chercher décideurs sur LinkedIn (Exa):
   `exa_search: "site:linkedin.com/in "CTO" OR "Directeur technique" "company_name""`

5. Mettre à jour Supabase:
   - website, contact_email, contact_phone
   - decision_maker_name, decision_maker_title
   - tech_stack (JSON), tags
```

#### Phase 3: Enrichissement Signaux d'Intention
**Outils**: Agent Reach (Twitter, Reddit, GitHub), Exa Search
**Coût**: $0

```
INPUT: Nom entreprise + site web + décideurs
OUTPUT: Signaux d'intention structurés

1. Recherche Twitter/X (Agent Reach):
   `twitter search: "company_name" OR "site:twitter.com company_name"`
   Signaux à détecter:
   - Annonces recrutement
   - Plaintes techniques
   - Annonces produits
   - Événements (salons, conférences)
   - Mentions concurrents

2. Recherche Reddit (Agent Reach):
   `reddit search: "company_name" OR "industry_keyword"`
   Signaux à détecter:
   - Discussions besoins
   - Recommandations prestataires
   - Problèmes techniques

3. Recherche GitHub (Agent Reach):
   `github repo search: "company_name" OR "company_domain"`
   Signaux à détecter:
   - Nouveaux repos (expansion tech)
   - Tech stack utilisé
   - Contributions open source

4. Recherche presse/actualités (Exa):
   `exa_search: "company_name funding OR raise OR series"`
   `exa_search: "company_name expansion OR new office OR hiring"`

5. Analyser et scorer signaux:
   Pour chaque signal:
   - Type: hiring_spree, pain_point, funding, expansion, tech_change
   - Source: twitter, reddit, github, press, job_board
   - Confiance: 0.0-1.0 (basé sur source et clarté)
   - Impact: 1-10 (sur probabilité conversion)
   - Date: timestamp découverte

6. Insérer dans intent_signals table
7. Recalculer intent_score du prospect
8. Mettre à jour Supabase
```

#### Phase 4: Vérification & Validation
**Outils**: Google Toolbox (execute_sql)
**Coût**: $0

```
1. Vérifier cohérence données:
   - SIRET valide (14 chiffres, clé Luhn)
   - Email format valide (si découvert)
   - Site web accessible (HTTP 200)
   - Décideur trouvé sur LinkedIn

2. Vérifier non-duplication:
   - SELECT siret, COUNT(*) FROM prospects GROUP BY siret HAVING COUNT(*) > 1
   - SELECT company_name, city, COUNT(*) FROM prospects GROUP BY company_name, city HAVING COUNT(*) > 1

3. Vérifier ICP fit:
   - NAF code dans liste cible
   - Effectif dans tranche cible
   - Localisation dans zone cible
   - Au moins 1 tech stack moderne détecté

4. Si échec vérification:
   - Flag prospect: is_verified = FALSE
   - Logger raison échec
   - Ne pas passer à outreach

5. Si succès:
   - Status: 'enriched' → 'qualified' (si fit >= 60)
   - Status: 'enriched' → 'hot_lead' (si intent >= 70)
   - Next action: planifier outreach
```

---

### MAPPING DES SIGNAUX → SCORE

| Signal | Type | Impact | Confiance Base |
|--------|------|--------|----------------|
| Levée de fonds > 1M€ | funding | 10 | 0.95 |
| Recrutement 5+ postes tech | hiring_spree | 9 | 0.90 |
| Plainte scaling/production | pain_point | 9 | 0.85 |
| Changement CTO | decision_change | 8 | 0.80 |
| Nouveau bureau/ expansion | expansion | 8 | 0.90 |
| Migration tech stack | tech_change | 7 | 0.75 |
| Budget IT mentionné | budget | 7 | 0.70 |
| Lancement nouveau produit | product_launch | 6 | 0.85 |
| Article besoin prestataire | intent_explicit | 10 | 0.90 |
| Concurrence switch mention | competitor_switch | 8 | 0.75 |

---

### MÉTRIQUES ENRICHISSEMENT

- **Taux de complétude**: >= 80% (website, email/phone, decision_maker, intent_signals)
- **Temps moyen enrichment**: < 4h par prospect
- **Taux de signaux détectés**: >= 40% des prospects enrichis
- **Taux de faux positifs signaux**: < 10% (vérifié manuellement sur échantillon)
- **Taux de duplication**: < 2%
