# Contexte Métier — stg_matches

## Objectifs

- **Finalité** : Fournir une table brute de tous les matchs sportifs disponibles, servant de point d'entrée pour tous les traitements liés aux performances des équipes et des pays.
- **Grain** : Une ligne par match unique.

## Transformations

- **Source** : Données brutes depuis une source externe contenant tous les matchs sportifs (équipes, scores, dates, lieux, arbitres, compétitions).
- **Transformation** :
    - Aucun calcul n'est effectué à ce stade.
    - Les colonnes sont recopiées telles quelles (pas de renommage, filtre ou transformation).
    - Les données conservent leur structure et format original.
- **Exclusions** : Aucune exclusion.

## Champs attendus

| Champ                  | Format | Nomenclature     | Règles/Tests                        |
| ---------------------- | ------ | ---------------- | ----------------------------------- |
| ID du match            | Entier | `match_id`       | Obligatoire, unique, clé primaire   |
| Équipe domicile (nom)  | Texte  | `home_team_name` | Obligatoire, non vide               |
| Équipe extérieur (nom) | Texte  | `away_team_name` | Obligatoire, non vide               |
| Score domicile         | Entier | `home_score`     | Obligatoire, valeur ≥ 0             |
| Score extérieur        | Entier | `away_score`     | Obligatoire, valeur ≥ 0             |
| Date du match          | Date   | `match_date`     | Obligatoire, format date valide     |
| Lieu/Stade             | Texte  | `venue`          | Optionnel, peut être NULL           |
| Arbitre                | Texte  | `referee`        | Optionnel, peut être NULL           |
| Compétition            | Texte  | `competition`    | Optionnel, contexte de la rencontre |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque match doit être identifié de façon unique par `match_id`.
    - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
    - `match_id`, `home_team_name`, `away_team_name`, `home_score`, `away_score`, `match_date` doivent être NOT NULL.
    - Les scores doivent être des entiers positifs ou zéro (pas de valeurs négatives).
    - Chaque match implique exactement deux équipes distinctes.
3. **Tests unitaires suggérés** :
    - Vérifier l'absence de doublons sur `match_id`.
    - Valider que les scores sont des entiers positifs.
    - Tester que `home_team_name` ≠ `away_team_name`.
    - Vérifier la distribution temporelle des matchs (continuité raisonnable des dates).

## Notes

- **Incertitudes** :
    - Les scores représentent-ils le temps réglementaire, les prolongations, ou les tirs au but ? Clarification nécessaire.
    - La fraîcheur des données n'est pas garantie (date de dernière mise à jour inconnue).
    - Le peuplement complet des compétitions et lieux n'est pas assuré.
- **Validation** : À compléter par [Nom du validateur] et [Date].
