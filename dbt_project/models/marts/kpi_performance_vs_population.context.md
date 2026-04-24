# Contexte Métier — kpi_performance_vs_population

## Objectifs

- **Finalité** : Calculer un KPI mesurant la performance sportive d'un pays rapportée à sa taille de population, permettant une comparaison équité.
- **Grain** : Une ligne par pays unique.

## Transformations

- **Source** : Jointure entre `fact_country_performance` (victoires) et `dim_population` (population).
- **Transformation** :
  - **Calcul du ratio** : `victoires ÷ population`
  - Plus le ratio est élevé, plus le pays est performant relativement à sa population.
  - Le résultat est un nombre très petit (ex: 0.0000003 pour 100 millions d'habitants avec 30 victoires).
  - Jointure sur le nom du pays (texte libre).
- **Exclusions** : Les pays avec population zéro ou NULL sont exclus (protection contre division par zéro).

## Champs attendus

| Champ       | Format  | Nomenclature        | Règles/Tests                                                |
| ----------- | ------- | ------------------- | ----------------------------------------------------------- |
| Nom du pays | Texte   | `country_name`      | Obligatoire, non vide, clé de jointure                      |
| Victoires   | Entier  | `wins`              | Obligatoire, valeur ≥ 0 (depuis `fact_country_performance`) |
| Population  | Entier  | `population_value`  | Obligatoire, valeur > 0 (non-zero pour division)            |
| KPI ratio   | Décimal | `performance_ratio` | Obligatoire, valeur = wins ÷ population, > 0                |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque pays doit apparaîtreune seule fois (unicité sur `country_name`).
   - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
   - `country_name`, `wins`, `population_value`, `performance_ratio` doivent être NOT NULL.
   - `population_value` doit être strictement > 0 (protection contre division par zéro).
   - `wins` doit être ≥ 0 (entier positif ou zéro).
   - `performance_ratio` doit vérifier : performance_ratio = wins ÷ population_value (calcul correct).
3. **Tests unitaires suggérés** :
   - Vérifier que la division par zéro ne se produit jamais (population_value > 0).
   - Valider le calcul du ratio sur un échantillon manuel de pays.
   - Affirmer que le nombre de lignes en sortie = nombre de pays avec performances ET population valides.
   - Vérifier que le classement par performance_ratio descendant est logique.

## Notes

- **Incertitudes** :
  - **Risque de doublons** : Si `dim_population` contient une ligne par année (pas filtré sur une année spécifique), chaque pays aura autant de lignes que d'années disponibles, faussant tous les totaux. **Quelle année de population utiliser ?** (ex: la plus récente, la moyenne ?)
  - **Risque d'erreur de division** : Si la population est zéro ou NULL dans les données sources, le calcul échouerait. Sous-entendu : une protection est en place (voir Exclusions), mais à vérifier.
  - **Le nombre de victoires peut être incorrect** (voir les incertitudes de `fact_country_performance`), ce qui invalide mécaniquement ce KPI.
  - Les pays peuvent être absents si leur nom est orthographié différemment entre `fact_country_performance` et `dim_population` (ex: "USA" vs "United States").
- **Validation** : À compléter par [Nom du validateur] et [Date]..
