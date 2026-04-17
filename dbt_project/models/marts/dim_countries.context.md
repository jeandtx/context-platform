# Contexte Métier — dim_countries

## Objectifs

- **Finalité** : Fournir une table de référence officielle des pays pour identifier et classifier uniformément les pays dans l'ensemble du projet.
- **Grain** : Une ligne par pays unique.

## Transformations

- **Source** : Données brutes de référence des pays avec noms complets et codes courts.
- **Transformation** :
    - Renommage simple des colonnes :
        - `Name` → `country_name`
        - `Code` → `iso2`
    - Aucun filtre, calcul ou déduplication supplémentaire.
    - Conservation de la structure de base.
- **Exclusions** : Aucune exclusion.

## Champs attendus

| Champ       | Format | Nomenclature   | Règles/Tests                                                             |
| ----------- | ------ | -------------- | ------------------------------------------------------------------------ |
| Nom du pays | Texte  | `country_name` | Obligatoire, non vide, nom complet du pays                               |
| Code ISO 2  | Texte  | `iso2`         | Obligatoire, format ISO 3166-1 alpha-2 (exactement 2 lettres majuscules) |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque pays doit apparaîttre une seule fois (unicité sur `country_name` et `iso2`).
    - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
    - Le nom du pays (`country_name`) ne doit jamais être NULL ou vide.
    - Le code ISO (`iso2`) doit contenir exactement 2 lettres majuscules (aA-Z).
    - Pas de caractères spéciaux ou espaces dans le code ISO.
3. **Tests unitaires suggérés** :
    - Vérifier l'absence de doublons sur `country_name` et `iso2`.
    - Valider le format ISO 2 (longueur exacte 2, caractères majuscules).
    - Affirmer que le nombre de lignes correspond au nombre de pays attendus.

## Notes

- **Incertitudes** :
    - La conformité au format ISO n'est pas automatiquement vérifiée dans le modèle.
    - Certains codes pourraient être incorrects ou en minuscules dans la source.
    - Couverture inconnue : tous les pays du monde sont-ils inclus ?
    - Fréquence de mise à jour de la source inconnue.
- **Validation** : À compléter par [Nom du validateur] et [Date].
