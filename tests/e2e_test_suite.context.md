# Contexte Métier — e2e_test_suite

## Objectifs

- **Finalité** : Fournir une suite de tests end-to-end complète validant l'intégrité fonctionnelle des transformations dbt et la cohérence des données critiques du projet, en couvrant les flux de données de bout en bout (brutes → staging → marts → KPIs).
- **Grain** : Une suite logique testant un flux métier complet (ex: données brutes → table de dimension → table de faits → KPI final), avec validation des invariants métier à chaque étape.

## Transformations

- **Source** : Infrastructure de test dbt complète (tests `.sql` dans `tests/`) combinée avec validations métier manuelles et assertions de couches.
- **Transformation** :
    - Orchestration de tests unitaires isolés par modèle (uniqueness, not_null, relationships, custom tests).
    - Enchaînement de tests de flux (tests de jointure multi-modèles, propagation des données, comportement attendu après transformations en cascade).
    - Validation des invariants métier (ex: `wins ≤ matches_played`, ratio de performance vérifié end-to-end).
    - Détection de régressions : comparaison avec baselines de données attendues.
    - Vérification des performances et du linting dbt.
- **Exclusions** :
    - Les tests de configuration intrinsèquement liés à un modèle (uniqueness, not_null) sont documentés dans chaque fichier `.context.md`.
    - Les tests d'infrastructure (déploiement, permission, réseau) ne font pas partie de cette suite.
    - Les tests unitaires de logique métier simple sont exclus (ex: test d'un renommage trivial).

## Champs attendus

| Champ             | Format        | Nomenclature        | Règles/Tests                                                                                          |
| ----------------- | ------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| Catégorie de test | Texte         | `test_category`     | Obligatoire, valeurs : "schema", "relationships", "invariants", "flows", "regressions", "performance" |
| Nom du test       | Texte         | `test_name`         | Obligatoire, non vide, describable (ex: "population_pivot_grain" ou "country_performance_sum_checks") |
| Modèles testés    | Texte (liste) | `models_tested`     | Obligatoire, liste de modèles impliqués (ex: `["stg_indicators", "dim_population"]`)                  |
| État du test      | Texte         | `status`            | Obligatoire, valeurs : "pass" (succès), "fail" (échec), "skip" (ignoré)                               |
| Résultat          | JSON          | `result_details`    | Optionnel, détails du test (assertions, comptages, valeurs attendues vs. réelles)                     |
| Date d'exécution  | DateTime      | `execution_date`    | Obligatoire, horodatage de l'exécution du test (UTC)                                                  |
| Temps d'exécution | Nombre (ms)   | `execution_time_ms` | Obligatoire, durée du test en millisecondes                                                           |

## Tests de logique métier

### 1. Vérification du grain

- **Suite de tests atomiques** : Chaque modèle dbt possède des tests isolés (uniqueness, not_null) documentés dans son `.context.md`.
- **Tests de flux** : S'assurer que chaque flux métier complet (raw → stg → mart → KPI) produit le grain attendu sans perte ni duplication de données.
    - Exemple : `stg_matches` (1 ligne/match unique) → `dim_matches` (1 ligne/match enrichi) → `fact_country_performance` (1 ligne/pays).
- **Absence de lignes orphelines** : Aucune ligne vide, NULL malveillant ou doublon en aval.

### 2. Validation des données

**Tests de schéma** :

- Toutes les colonnes attendues (déclarées dans `.context.md` section "Champs attendus") doivent être présentes dans le modèle.
- Les types de données SQL doivent correspondre aux formats déclarés.
- Aucune colonne inattendue ne doit soudainement apparaître.

**Tests de contraintes NOT NULL** :

- Chaque colonne marquée "Obligatoire" ne doit contenir aucune valeur NULL.
- Les colonnes "Optionnel" peuvent contenir des NULL mais doivent être cohérentes.

**Tests de valeurs valides** :

- Les énumérations (ex: genre ∈ {"Male", "Female", "Mixed"}) doivent être respectées.
- Les types numériques doivent être non-négatifs (ex: scores, populations).
- Les plages de valeurs doivent être valides (ex: année ∈ [1960, 2025]).

**Tests de relations** :

- Toutes les clés étrangères doivent référencer des lignes existantes dans les tables parent.
- Exemple : Chaque `team_id` dans `dim_matches` doit exister dans `dim_teams`.

**Tests de contraintes logiques inter-champs** :

- `wins ≤ matches_played` dans `fact_country_performance`.
- `performance_ratio = wins ÷ population` dans `kpi_performance_vs_population`.
- Si `home_score > away_score`, alors `winner = home_team`.

### 3. Tests unitaires suggérés

#### 3.1 Catégorie "Schema"

```sql
-- Tous les champs attendus sont présents
-- Type de données correcte
-- Pas de colonnes supplémentaires inattendues
```

#### 3.2 Catégorie "Relationships" (Intégrité référentielle)

```
- stg_matches.team_id → dim_teams.team_id
- dim_team_country.team_id → dim_teams.team_id
- kpi_performance_vs_population.country_name → dim_countries.country_name ou dim_population.country_name
```

#### 3.3 Catégorie "Invariants" (Logique métier garantie)

```
- dim_matches: winner ∈ {home_team, away_team, "draw"}
- dim_matches: (home_score > away_score) → (winner = home_team)
- fact_country_performance: wins ≤ matches_played
- kpi_performance_vs_population: population_value > 0 (division par zéro)
- dim_teams: team_gender ∈ {"Male", "Female", "Mixed"}
```

#### 3.4 Catégorie "Flows" (Flux complets)

```
Flux 1 : Raw → Staging → Marts
  stg_indicators (pivot) → dim_population (1 ligne/pays/année)

Flux 2 : Équipes → Performances → KPI
  stg_matches → dim_matches → dim_team_country → fact_country_performance → kpi_performance_vs_population

Tests :
  - Comptage des matchs préservé après transformations (avec perte documentée si applicable)
  - Agrégation par pays correcte (pas de double comptage)
  - Ratio KPI calculé sans erreur de division
```

#### 3.5 Catégorie "Regressions" (Baseline de données)

```
Comparer la distribution des données actuelles à une baseline connue :
  - Nombre total de pays: doit être stable (±1%)
  - Distribution des victoires: doit suivre pattern historique
  - Absence de NULL anormal: comparer avant/après transformation
```

#### 3.6 Catégorie "Performance"

```
- Temps d'exécution de dbt run : < [seuil défini] secondes
- Taille des tables générées : < [seuil défini] MB
- Aucune requête N+1 ou scan table complète inutile
```

## Notes

- **Incertitudes** :
    - **Baseline de régression inconnue** : Pas de snapshot de données attendues documenté. À générer après validation initiale.
    - **Seuils de performance non définis** : À établir après premières exécutions en production.
    - **Couverture de tests incompète potentiellement** : Certains flux métier complexes (ex: jointures multi-niveaux) peuvent ne pas être couverts par les tests actuels.
    - **Fragilité des tests de correspondance textuelle** : Les tests validant la correspondance équipe-pays (via `dim_team_country`) reposent sur matching textuel fragile. Risque de faux négatifs (équipes orphelines non détectées).
    - **Dépendances implicites entre modèles** : Certains modèles peuvent avoir des dépendances implicites non documentées (ex: ordre d'exécution de `dbt run` attendu). À clarifier.
    - **Validation manuelle requise** : Les tests automatisés ne peuvent valider que les contraintes formelles. Les règles métier nuancées (ex: "Les scores représentent le temps réglementaire") requièrent une validation manuelle.

- **Directives de mise à jour** :
    - Lorsqu'un nouveau modèle est ajouté, ajouter des tests "Relationships" et "Invariants" correspondants.
    - Lorsqu'une transformation métier change, mettre à jour les tests "Flows" et considérer une nouvelle baseline "Regressions".
    - Maintenir cette suite à jour avec les changements métier : exécuter avant chaque commit/PR.
    - Documenter les anomalies acceptées (ex: absence intentionnelle de certaines équipes).

- **Validation** : À compléter par [Nom du responsable Tests] et [Date de certification].

## Structuration des fichiers de tests

Les tests end-to-end sont organisés dans la structure suivante :

```
dbt_project/
├── tests/
│   ├── e2e/
│   │   ├── test_schema_integrity.sql         ← Vérification de schéma
│   │   ├── test_relationships_integrity.sql  ← Intégrité référentielle
│   │   ├── test_business_invariants.sql      ← Invariants métier
│   │   ├── test_data_flows.sql               ← Flux de données complets
│   │   ├── test_regressions.sql              ← Comparaisons de baseline
│   │   └── test_performance.sql              ← Benchmarks de performance
│   └── generic/
│       ├── is_valid_enum.sql                 ← Tests génériques réutilisables
│       ├── has_valid_grain.sql
│       └── ...
├── seeds/
│   └── baseline_data.csv                     ← Données de baseline (optionnel)
└── e2e_test_suite.context.md                 ← Ce fichier (orchestration)
```

## Exécution de la suite de tests

```bash
# Exécuter tous les tests
dbt test

# Exécuter uniquement les tests E2E
dbt test --select tag:e2e

# Interroger les résultats
dbt test --select tag:e2e --store-failures
# Les résultats sont stockés dans target/failing_tests.sql
```

## Vue d'ensemble des flux testés

```
                stg_indicators (brutes)
                       ↓ [Pivot + conversion]
                dim_population (dimension)
                       ↑
                       | [Jointure]
                       ↓
              fact_country_performance
                       ↓ [Division]
         kpi_performance_vs_population

                stg_matches (brutes)
                       ↓ [Calcul winner]
                 dim_matches (dimension)
                ↙              ↘
    dim_teams              dim_team_country
       ↑                         ↑
       └─────────┬───────────────┘
                  | [Jointure]
                  ↓
        fact_country_performance
                  ↓ [Division]
       kpi_performance_vs_population
```

**Chaque flèche doit avoir des tests de validation** :

- ✓ Schéma préservé
- ✓ Grain respecté
- ✓ Aucune perte/duplication
- ✓ Contraintes métier appliquées
