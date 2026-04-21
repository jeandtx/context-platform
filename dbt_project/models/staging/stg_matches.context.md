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

| Champ                           | Format   | Nomenclature            | Règles/Tests                              |
| ------------------------------- | -------- | ----------------------- | ----------------------------------------- |
| ID du match                     | Entier   | `match_id`              | Obligatoire, unique, clé primaire         |
| Date du match                   | Date     | `match_date`            | Obligatoire, format date valide           |
| Heure de coup d'envoi           | Texte    | `kick_off`              | Optionnel, peut être NULL                 |
| Score domicile                  | Entier   | `home_score`            | Obligatoire, valeur ≥ 0                   |
| Score extérieur                 | Entier   | `away_score`            | Obligatoire, valeur ≥ 0                   |
| Statut du match                 | Texte    | `match_status`          | Optionnel (ex: available, collecting)     |
| Statut 360 du match             | Texte    | `match_status_360`      | Optionnel                                 |
| Journée de championnat          | Entier   | `match_week`            | Optionnel                                 |
| Dernière mise à jour            | Datetime | `last_updated`          | Optionnel                                 |
| Dernière mise à jour 360        | Datetime | `last_updated_360`      | Optionnel                                 |
| ID compétition                  | Entier   | `competition_id`        | Obligatoire                               |
| Nom compétition                 | Texte    | `competition_name`      | Obligatoire                               |
| Pays compétition                | Texte    | `competition_country`   | Optionnel                                 |
| ID saison                       | Entier   | `season_id`             | Obligatoire                               |
| Nom saison                      | Texte    | `season_name`           | Obligatoire                               |
| ID équipe domicile              | Entier   | `home_team_id`          | Obligatoire                               |
| Équipe domicile (nom)           | Texte    | `home_team_name`        | Obligatoire, non vide                     |
| Genre équipe domicile           | Texte    | `home_team_gender`      | Optionnel (ex: male, female)              |
| Pays équipe domicile            | Texte    | `home_team_country`     | Optionnel                                 |
| ID équipe extérieure            | Entier   | `away_team_id`          | Obligatoire                               |
| Équipe extérieure (nom)         | Texte    | `away_team_name`        | Obligatoire, non vide                     |
| Genre équipe extérieure         | Texte    | `away_team_gender`      | Optionnel (ex: male, female)              |
| Pays équipe extérieure          | Texte    | `away_team_country`     | Optionnel                                 |
| ID phase de compétition         | Entier   | `competition_stage_id`  | Optionnel                                 |
| Nom phase de compétition        | Texte    | `competition_stage_name`| Optionnel (ex: Group Stage, Final)        |
| ID stade                        | Entier   | `stadium_id`            | Optionnel                                 |
| Nom stade                       | Texte    | `stadium_name`          | Optionnel                                 |
| Pays stade                      | Texte    | `stadium_country`       | Optionnel                                 |
| ID arbitre                      | Entier   | `referee_id`            | Optionnel                                 |
| Nom arbitre                     | Texte    | `referee_name`          | Optionnel                                 |
| Pays arbitre                    | Texte    | `referee_country`       | Optionnel                                 |
| Version des données             | Texte    | `data_version`          | Optionnel                                 |

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
