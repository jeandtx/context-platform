# Contexte Métier — stg_indicators

## Objectifs

- **Finalité** : Fournir les données d'indicateurs mondiaux (notamment population) par pays en format "large" (une colonne par année) comme source brute pour les transformations ultérieures.
- **Grain** : Une ligne par pays, avec colonnes représentant les années 1960–2025.

## Transformations

- **Source** : Données brutes depuis une source externe (type Banque Mondiale) contenant des indicateurs socio-économiques globaux.
- **Transformation** :
    - Aucune transformation n'est appliquée à ce stade.
    - Les données sont recopiées telles quelles, en format "large" (une colonne par année).
    - La mise en forme vers format "long" (une ligne par année) se fera dans le modèle `dim_population`.
- **Exclusions** : Aucune exclusion.

## Champs attendus

| Champ             | Format          | Nomenclature     | Règles/Tests                                                     |
| ----------------- | --------------- | ---------------- | ---------------------------------------------------------------- |
| Nom du pays       | Texte           | `Country Name`   | Obligatoire, issu de la source brute                             |
| Code du pays      | Texte           | `Country Code`   | Obligatoire, code ISO ou code interne                            |
| Code indicateur   | Texte           | `Indicator Code` | Obligatoire (ex: SP.POP.TOTL pour population)                    |
| Nom indicateur    | Texte           | `Indicator Name` | Obligatoire (ex: "Population, total")                            |
| Colonnes d'années | Numérique/Texte | `1960` à `2025`  | Une colonne par année, valeur numérique ou vide (NULL implicite) |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque ligne doit correspondre à un pays unique pour un indicateur donné.
    - Aucune ligne vide autorisée pour les champs de base (`Country Name`, `Indicator Code`).
2. **Validation des données** :
    - Les colonnes d'années (1960–2025) doivent être présentes (même si vides).
    - Les valeurs de population doivent être numériques ou vides (NULL).
    - Une valeur vide signifie "donnée non disponible", pas "population zéro".
3. **Tests unitaires suggérés** :
    - Vérifier la complétude des colonnes d'années (1960–2025 présentes).
    - Valider que les valeurs numériques sont positives ou NULL.
    - Tester l'absence de doublons par (Country Name, Indicator Code) combinaison.

## Notes

- **Incertitudes** :
    - La source pourrait contenir d'autres types d'indicateurs que la population ; filtrage nécessaire en aval.
    - Le taux de données manquantes par pays et par période n'est pas connu.
    - Format d'entrée "large" requiert une transformation significative en aval pour exploitation.
- **Validation** : À compléter par [Nom du validateur] et [Date].
