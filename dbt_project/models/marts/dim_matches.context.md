# Contexte Métier — dim_matches

## Objectifs

- **Finalité** : Fournir une table de dimension des matchs avec équipes, scores et détermination du vainqueur ou match nul.
- **Grain** : Une ligne par match unique.

## Transformations

- **Source** : Données brutes depuis `stg_matches` avec équipes et scores.
- **Transformation** :
  - Renommage des colonnes :
    - `home_team_name` → `home_team`
    - `away_team_name` → `away_team`
  - **Calcul du vainqueur** : Comparaison des scores :
    - Si score domicile > score extérieur → vainqueur = nom de l'équipe domicile
    - Si score extérieur > score domicile → vainqueur = nom de l'équipe extérieure
    - Si égalité → vainqueur = "draw"
  - Conservation des autres colonnes (dates, lieux, compétitions).
- **Exclusions** : Aucune exclusion.

## Champs attendus

| Champ            | Format | Nomenclature | Règles/Tests                                               |
| ---------------- | ------ | ------------ | ---------------------------------------------------------- |
| ID du match      | Entier | `match_id`   | Obligatoire, unique, clé primaire                          |
| Équipe domicile  | Texte  | `home_team`  | Obligatoire, non vide, renommé depuis `home_team_name`     |
| Équipe extérieur | Texte  | `away_team`  | Obligatoire, non vide, renommé depuis `away_team_name`     |
| Score domicile   | Entier | `home_score` | Obligatoire, valeur ≥ 0                                    |
| Score extérieur  | Entier | `away_score` | Obligatoire, valeur ≥ 0                                    |
| Vainqueur        | Texte  | `winner`     | Obligatoire, valeur = nom d'équipe ou "draw" (jamais NULL) |
| Date du match    | Date   | `match_date` | Optionnel, peut être NULL                                  |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque match doit être identifié de façon unique par `match_id`.
   - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
   - `match_id`, `home_team`, `away_team`, `home_score`, `away_score`, `winner` doivent être NOT NULL.
   - La valeur du champ `winner` doit être soit le nom d'une équipe (home_team ou away_team), soit la valeur "draw".
   - Les scores doivent être des entiers positifs ou zéro.
   - Si home_score > away_score, alors winner doit être home_team.
   - Si away_score > home_score, alors winner doit être away_team.
   - Si home_score == away_score, alors winner doit être "draw".
3. **Tests unitaires suggérés** :
   - Vérifier l'absence de doublons sur `match_id`.
   - Valider que home_team ≠ away_team pour chaque ligne.
   - Affirmer que la logique de calcul du vainqueur est correcte par comparaison d'un échantillon représentatif.
   - Compter le nombre de victoires, égalités et vérifier les proportions sont raisonnables.

## Notes

- **Incertitudes** :
  - **Les scores représentent-ils le temps réglementaire, les prolongations, ou les tirs au but ?** Impact direct sur le calcul du vainqueur.
  - Les données source contiennent-elles tous les matchs attendus ?
  - La complaisance des doublons dans la source brute n'est pas contrôlée.
- **Validation** : À compléter par [Nom du validateur] et [Date].
