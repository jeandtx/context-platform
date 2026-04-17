# Contexte Métier — dim_teams

## Objectifs

- **Finalité** : Fournir une table de référence des équipes sportives avec leurs caractéristiques (genre, pays d'origine).
- **Grain** : Une ligne par équipe unique.

## Transformations

- **Source** : Données depuis `stg_matches` colonne "equipe domicile" avec informations sur le genre et le pays.
- **Transformation** :
    - Extraction des équipes apparaissant en tant qu'equipe domicile.
    - Déduplication : si une équipe a joué plusieurs matchs à domicile, elle n'apparaît qu'une fois.
    - Conservation de l'identifiant d'équipe, nom, genre et information de pays.
- **Exclusions** : Les équipes qui n'ont jamais joué à domicile sont absentes de cette table.

## Champs attendus

| Champ      | Format | Nomenclature   | Règles/Tests                                                |
| ---------- | ------ | -------------- | ----------------------------------------------------------- |
| ID équipe  | Entier | `team_id`      | Obligatoire, unique, clé primaire                           |
| Nom équipe | Texte  | `team_name`    | Obligatoire, non vide, unique                               |
| Genre      | Texte  | `team_gender`  | Obligatoire, valeurs autorisées : "Male", "Female", "Mixed" |
| Pays       | Texte  | `team_country` | Obligatoire, non vide, identifiant du pays d'origine        |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque équipe doit apparaître une seule fois (unicité sur `team_id` et `team_name`).
    - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
    - `team_id`, `team_name`, `team_gender`, `team_country` doivent être NOT NULL.
    - Le genre doit être l'une des valeurs autorisées : "Male", "Female" ou "Mixed" (casse respectée).
    - Le pays doit correspondre à un pays valide (vérifier contre la table dim_countries).
3. **Tests unitaires suggérés** :
    - Vérifier l'absence de doublons sur `team_id` et `team_name`.
    - Valider que le genre ne contient que les valeurs autorisées.
    - Affirmer que chaque équipe a au moins joué un match à domicile.
    - Vérifier la jointure avec dim_countries sur `team_country` (certains pays peuvent être manquants).

## Notes

- **Incertitudes** :
    - **Les équipes qui n'ont jamais joué à domicile sont absentes de cette table.** Si une équipe n'apparaît qu'en tant qu'équipe extérieure dans la source, elle ne sera pas référencée ici. Cela crée un biais d'analyse.
    - La représentation complète des équipes n'est pas garantie.
    - La classification de genre peut ne pas être à jour avec les évolutions compétition.
- **Validation** : À compléter par [Nom du validateur] et [Date].
