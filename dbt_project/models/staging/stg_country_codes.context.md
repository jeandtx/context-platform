# Contexte Métier — stg_country_codes

## Objectifs

- **Finalité** : Fournir une table de référence des pays du monde pour identifier et classifier tous les pays utilisés dans le projet.
- **Grain** : Une ligne par pays (source non transformée).

## Transformations

- **Source** : Fichier de référence externe contenant les noms de pays et leurs codes ISO.
- **Transformation** :
  - Aucune transformation majeure n'est effectuée.
  - Renommage simple : `Name` → `country_name`, `Code` → `code`.
  - Les données sont recopiées telles quelles depuis la source brute.
- **Exclusions** : Aucune exclusion, toutes les lignes sources sont conservées.

## Champs attendus

| Champ       | Format | Nomenclature | Règles/Tests                                                  |
| ----------- | ------ | ------------ | ------------------------------------------------------------- |
| Nom du pays | Texte  | `name`       | Obligatoire, non vide, issu de la source brute                |
| Code ISO    | Texte  | `code`       | Obligatoire, format ISO 3166-1 alpha-2 (2 lettres majuscules) |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque pays doit apparaître une seule fois (unicité sur `country_name` et `code`).
   - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
   - Le nom du pays (`country_name`) ne doit jamais être NULL ou vide.
   - Le code ISO (`code`) doit contenir exactement 2 lettres majuscules.
3. **Tests unitaires suggérés** :
   - Vérifier l'absence de doublons sur `country_name` et `code`.
   - Valider que le code ISO respecte le format (longueur 2, caractères majuscules).
   - Tester la couverture : nombre attendu de pays comparé au nombre réel.

## Notes

- **Incertitudes** :
  - La conformité exacte au format ISO n'est pas vérifiée automatiquement dans le modèle.
  - On ne sait pas si la liste couvre tous les pays du monde ni à quelle fréquence elle est mise à jour.
  - Certains codes pourraient être incorrects ou en minuscules.
- **Validation** : À compléter par [Nom du validateur] et [Date].
