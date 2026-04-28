# Contexte Métier — fct_teams_by_country

## Objectifs

- **Finalité** : Fournir une agrégation du nombre d'équipes uniques par pays pour analyser la distribution géographique des équipes.
- **Grain** : Une ligne par pays avec au moins une équipe.
- **Cas d'usage** : Visualisation BI montrant la concentration des équipes par pays, identification des pays dominants.

## Transformations

- **Source** : `dim_teams` (table de référence des équipes).
- **Transformation** :
  - Déduplique les équipes par `team_id` pour éviter les comptes multiples.
  - Groupe par `team_country`.
  - Compte le nombre distinct d'équipes (`num_teams`) et de noms uniques (`num_unique_team_names`) par pays.
  - Exclusion des valeurs NULL dans `team_country`.
  - Tri décroissant par nombre d'équipes (pays avec le plus d'équipes en premier).
- **Exclusions** : Pays sans équipes (valeurs NULL).

## Champs attendus

| Champ                      | Format  | Nomenclature           | Règles/Tests                                                  |
| -------------------------- | ------- | ---------------------- | ------------------------------------------------------------- |
| Pays                       | Texte   | `country`              | Obligatoire, non vide, nom ou code du pays.                   |
| Nombre d'équipes           | Entier  | `num_teams`            | >= 1, COUNT DISTINCT de `team_id`.                            |
| Nombre de noms uniques     | Entier  | `num_unique_team_names`| >= 1, COUNT DISTINCT de `team_name`.                          |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque pays doit apparaître une seule fois.
   - Aucun doublon sur `country`.
   - `num_teams` >= `num_unique_team_names` (logique naturelle).

2. **Validation des données** :
   - `country` ne doit jamais être NULL ou vide.
   - `num_teams` doit être un entier positif (>= 1).
   - `num_unique_team_names` doit être un entier positif (>= 1).

3. **Tests unitaires suggérés** :
   - Absence de doublons sur `country`.
   - `num_teams` > 0 pour toutes les lignes.
   - Total des équipes dans fct_teams_by_country == nombre distinct d'équipes dans dim_teams.
   - Vérifier que `num_teams` >= `num_unique_team_names` (logique de dédoublonnage).

## Notes

- **Dépendances** : `dim_teams` doit être complète et à jour.
- **Incertitudes** :
  - La normalisation des noms de pays peut varier (codes ISO vs noms complets).
  - Certaines équipes peuvent avoir `team_country` NULL dans la source.
- **Performance** : Agrégation simple, peu de lignes (~250 pays max), pas de bottleneck attendu.
- **Validation** : À compléter par [Responsable BI] et [Date].
