# Contexte Métier — dim_population

## Objectifs

- **Finalité** : Fournir une table de population annuelle par pays (1960–2025) pour rapporter les performances sportives en fonction de la taille de la population.
- **Grain** : Une ligne par combinaison **pays + année**.

## Transformations

- **Source** : Données en format "large" (une colonne par année).
- **Transformation** :
  - Pivot des données pour obtenir un format "long" (une ligne par pays/année).
  - Conversion des années en entier pour permettre filtres et comparaisons.
  - Les valeurs de population non lisibles sont ignorées (converties en NULL, puis exclues).
- **Exclusions** : Les années sans données de population sont absentes du résultat final.

## Champs attendus

| Champ                | Format          | Nomenclature       | Règles/Tests                                                                 |
| -------------------- | --------------- | ------------------ | ---------------------------------------------------------------------------- |
| Nom du pays          | Texte           | `country_name`     | Obligatoire, issu de `"Country Name"`                                        |
| Code du pays         | Texte           | `country_code`     | Obligatoire, issu de `"Country Code"`                                        |
| Nom de l'indicateur  | Texte           | `indicator_name`   | Obligatoire, doit être "Population totale" (vérification manuelle)           |
| Code de l'indicateur | Texte           | `indicator_code`   | Obligatoire, issu de `"Indicator Code"`                                      |
| Année                | Entier          | `year`             | Obligatoire, converti en entier (ex: "1960" → 1960)                          |
| Population           | Entier (bigint) | `population_value` | Obligatoire, valeur brute (non arrondie), NULL si non disponible ou invalide |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque ligne doit correspondre à une combinaison unique **pays + année**.
   - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
   - Seules les lignes avec `indicator_name = "Population totale"` doivent être conservées.
   - Les valeurs NULL ou non convertibles en bigint sont exclues.
3. **Couverture temporelle** :
   - Les années manquantes par pays ne génèrent pas de ligne vide (vérifier l’absence de trous dans les données attendues).
4. **Tests unitaires suggérés** :
   - Vérifier que le nombre de lignes en sortie = nombre de pays × nombre d’années avec données valides.
   - Tester la conversion des années (ex: "2025" → 2025).
   - Valider l’exclusion des valeurs NULL après pivot.

## Notes

- **Incertitudes** :
  - Risque d’inclusion d’autres indicateurs (ex: taux de natalité) si la source n’est pas filtrée en amont.
  - Comportement variable sur les NULL selon l’environnement technique (à documenter).
- **Validation** : À compléter par [Nom du validateur] et [Date].
