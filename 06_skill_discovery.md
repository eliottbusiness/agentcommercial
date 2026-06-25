# SKILL: Discovery & Prospection
## Version: 1.0 | Agent Commercial Autonome

---

### OBJECTIF
Découvrir des prospects qualifiés en utilisant uniquement des sources gratuites et open source. 
**Règle d'or**: Qualité > Quantité. Max 50 nouveaux prospects/jour, min 70% de fit ICP.

---

### SOURCES DE DÉCOUVERTE (100% GRATUITES)

#### 1. SIRENE API (via DataGouv MCP)
**Endpoint**: `https://mcp.data.gouv.fr/mcp` → `search_datasets` / `query_resource_data`
**Rate limit**: 30 req/min (INSEE)
**Coût**: $0

**Workflow**:
```
1. Rechercher dataset "Sirene" via search_datasets
2. Lister ressources via list_dataset_resources
3. Query data via query_resource_data avec filtres:
   - NAF code: [62.01Z, 62.02A, 62.03Z, 63.11Z, 63.12Z]
   - Tranche effectif: [11-20, 21-50, 51-100, 101-250]
   - Date création: > 2 ans, < 15 ans
   - Localisation: Paris, Lyon, Marseille, Toulouse, Bordeaux
4. Pour chaque entreprise: extraire SIREN, SIRET, raison sociale, forme juridique, NAF, adresse, effectif
5. Vérifier unicité SIRET avant insertion Supabase
```

**Requête Overpass QL exemple**:
```
[out:json][timeout:60];
area["name"="Paris"]->.searchArea;
(
  node["office"="company"](area.searchArea);
  way["office"="company"](area.searchArea);
  relation["office"="company"](area.searchArea);
);
out body;
>;
out skel qt;
```

#### 2. Overpass API (OpenStreetMap)
**Endpoint**: `https://overpass-api.de/api/interpreter`
**Rate limit**: ~10 000/jour recommandé
**Coût**: $0

**Workflow**:
```
1. Construire requête Overpass QL pour zone géographique
2. Filtrer par catégorie: office=company, shop=*, amenity=restaurant|café|hotel
3. Extraire: name, addr:*, website, phone, opening_hours
4. Géocoder si nécessaire
5. Croiser avec SIRENE pour enrichir SIRET/NAF
6. Insérer dans Supabase avec source='overpass'
```

**Catégories d'intérêt pour B2B**:
- `office=company` (bureaux entreprises)
- `office=it` (bureaux IT)
- `office=software` (éditeurs logiciel)
- `shop=electronics` (revendeurs tech)
- `amenity=restaurant` (restauration - pour sectoriel)

#### 3. Exa Search (via MCP)
**Endpoint**: `https://mcp.exa.ai/mcp`
**Rate limit**: 150 calls/jour (unauthenticated)
**Coût**: $0

**Workflow**:
```
1. Recherche sémantique: "startups SaaS France levée fonds 2026"
2. Filtrer par catégorie: company
3. Extraire: nom, site web, description, localisation, effectif
4. Recherche similaire (find_similar) pour expansion
5. Enrichir avec contenu site web (exa_contents)
6. Insérer dans Supabase avec source='exa_search'
```

**Requêtes Exa optimisées**:
- `"SaaS startups France hiring developers 2026"`
- `"digital transformation consulting Paris PME"`
- `"cloud infrastructure companies Lyon scale"`
- `"AI agencies Marseille recruitment tech"`

#### 4. Agent Reach (Web Scraping)
**Outils**: `agent-reach web`, `agent-reach exa_search`
**Coût**: $0 (Jina Reader gratuit)

**Workflow**:
```
1. Identifier pages d'annuaires sectoriels (ex: French Tech, La French Fab)
2. Lire pages via Jina Reader: `curl https://r.jina.ai/URL`
3. Extraire liste entreprises
4. Pour chaque entreprise: chercher site web via Exa
5. Scraper site web pour signaux d'intention
6. Insérer dans Supabase
```

---

### CRITÈRES DE QUALITÉ (Filtrage avant insertion)

Avant d'insérer un prospect dans Supabase, VÉRIFIER:

1. **Unicité**: `SELECT COUNT(*) FROM prospects WHERE siret = $siret` = 0
2. **ICP Fit**: Au moins 3/5 critères ICP matchés
3. **Signaux positifs**: Au moins 1 signal d'intention détecté OU entreprise en croissance
4. **Contactabilité**: Site web OU email détectable OU présence LinkedIn
5. **Non concurrent**: Vérifier que ce n'est pas un concurrent direct

**Si échec**: Logger dans `rejected_prospects` avec raison pour analyse.

---

### MÉTRIQUES DISCOVERY

- **Daily quota**: 50 prospects max/jour
- **Target quality**: >= 70% fit ICP
- **Target enrichment**: 100% des prospects découverts enrichis sous 24h
- **Target signal detection**: >= 30% des prospects avec signal détecté
