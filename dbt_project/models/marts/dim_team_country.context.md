# Contexte Métier — dim_team_country

## Objectifs

- **Finalité** : Fournir une table de correspondance entre équipes et pays pour permettre l'agrégation des performances des équipes par pays.
- **Grain** : Une ligne par combinaison équipe-pays unique.

## Transformations

- **Source** : Données depuis `dim_teams` avec noms d'équipes et la référence pays.
- **Transformation** :
    - **Correspondance textuelle** : Veérification si le nom du pays apparaît dans le nom de l'équipe (matching de texte).
    - La correspondance est volontairement fragile (par construction, notée dans le code source).
    - Conservation de l'ID d'équipe, nom d'équipe et nom du pays.
- **Exclusions** : Les équipes dont le nom ne contient pas le nom d'un pays seront perdues.

## Champs attendus

| Champ      | Format | Nomenclature   | Règles/Tests                                |
| ---------- | ------ | -------------- | ------------------------------------------- |
| ID équipe  | Entier | `team_id`      | Obligatoire, clé étrangère vers `dim_teams` |
| Nom équipe | Texte  | `team_name`    | Obligatoire, non vide                       |
| Nom pays   | Texte  | `country_name` | Obligatoire, trouvé par matching textuel    |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque équipe doit être associée à un seul pays (unicité sur `team_id`).
    - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
    - `team_id`, `team_name`, `country_name` doivent être NOT NULL.
    - Chaque `team_id` doit correspondre à une équipe existante dans `dim_teams`.
    - Le pays doit pouvoir être trouvé dans `dim_countries` (verification recommandée en aval).
3. **Tests unitaires suggérés** :
    - Vérifier que le matching textuel est validé: "France Women" doit correspondre à "France".
    - Identifier les équipes de `dim_teams` qui ne sont PAS présentes ici (matching échoué).
    - Vérifier l'absence de doublons sur `team_id`.

## Notes

- **Incertitudes** :
    - **Ce lien est volontairement fragile** (d'après le code source). Les équipes dont le nom ne contient pas le pays seront perdues.
    - Une équipe pourrait correspondre à plusieurs pays si son nom contient plusieurs noms de pays (ex: "USA Women" si "USA" et "Women" sont des noms de pays — peu probable mais possible).
    - La méthode de correspondance (texte libre) est très sensible aux fautes d'orthographe et aux variantes de noms (ex: "USA" vs "United States", "England" vs "United Kingdom").
    - Pas de mécanisme de fallback pour les équipes non appariées.
- **Validation** : À compléter par [Nom du validateur] et [Date].
