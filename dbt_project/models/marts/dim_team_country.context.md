# Contexte Métier — dim_team_country

## Objectifs

- **Finalité** : Fournir une table de correspondance entre équipes et pays pour permettre l'agrégation des performances des équipes par pays.
- **Grain** : Une ligne par équipe unique (`team_id`). Chaque équipe est associée à au plus un pays.

## Transformations

- **Source** : `dim_teams` (identifiant, nom, code pays structuré) et `dim_countries` (référentiel pays avec codes ISO2).
- **Transformation** :
    - **Stratégie principale — jointure structurelle** : Jointure directe entre `dim_teams.team_country` (code pays issu de la source) et `dim_countries.iso2`. Ce champ est une clé étrangère structurée présente dans les données sources et doit être utilisé en priorité.
    - **Stratégie de repli — matching textuel** : Pour les équipes dont `team_country` ne correspond à aucune entrée dans `dim_countries.iso2`, tentative de correspondance par comparaison textuelle entre `team_name` et `country_name` (insensible à la casse, `LIKE '%country_name%'`). Cette méthode est moins fiable et sert uniquement de filet de sécurité.
    - **Déduplication** : Si la stratégie de repli produit plusieurs pays pour une même équipe, conserver le pays avec le nom le plus long (correspondance la plus spécifique). Cela préserve le grain `team_id → 1 pays`.
- **Exclusions** : Les équipes pour lesquelles aucune des deux stratégies ne produit de correspondance conservent `country_name = NULL` et `iso2 = NULL` (LEFT JOIN). Elles restent visibles dans la table pour diagnostic.

## Champs attendus

| Champ      | Format | Nomenclature   | Règles/Tests                                                                    |
| ---------- | ------ | -------------- | ------------------------------------------------------------------------------- |
| ID équipe  | Entier | `team_id`      | Obligatoire, unique, clé primaire, issu de `dim_teams`                          |
| Nom équipe | Texte  | `team_name`    | Obligatoire, non vide                                                           |
| Nom pays   | Texte  | `country_name` | Optionnel, NULL si aucune correspondance trouvée, issu de `dim_countries`       |
| Code ISO2  | Texte  | `iso2`         | Optionnel, NULL si aucune correspondance trouvée, code pays à 2 lettres (ISO 3166-1) |
| Méthode    | Texte  | `match_method` | Optionnel, valeurs : `'iso2'` (jointure directe), `'text'` (repli textuel), NULL (aucune correspondance) |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque équipe doit apparaître exactement une fois (unicité sur `team_id`).
    - Aucun doublon sur `team_id` n'est toléré.
2. **Validation des données** :
    - `team_id` et `team_name` doivent être NOT NULL.
    - `country_name` et `iso2` sont cohérents : si l'un est NULL, l'autre l'est aussi.
    - `match_method` ne peut contenir que `'iso2'`, `'text'` ou NULL.
    - Le taux de correspondance via stratégie principale (`match_method = 'iso2'`) doit être majoritaire (> 80 % des équipes).
3. **Tests unitaires suggérés** :
    - Vérifier l'absence de doublons sur `team_id`.
    - Vérifier que "France Women" est associée à "France" (validation stratégie principale ou repli).
    - Vérifier que le nombre d'équipes avec `country_name IS NULL` reste stable dans le temps (alarme si augmentation).
    - Valider que toutes les équipes avec `match_method = 'iso2'` ont un `iso2` valide référencé dans `dim_countries`.

## Notes

- **Incertitudes** :
    - Le champ `team_country` de `dim_teams` est issu de `home_team_country` dans les données sources brutes. Sa complétude et sa cohérence avec les codes ISO2 de `dim_countries` ne sont pas garanties ; des écarts de format (ex. code à 3 lettres vs 2 lettres, valeur vide) peuvent forcer le repli textuel pour certaines équipes.
    - La stratégie de repli textuel reste sensible aux variantes de noms (ex. "USA" ne correspondra pas à "United States"). Les équipes concernées auront `country_name = NULL` sauf si leurs noms contiennent exactement le libellé de `dim_countries`.
    - Les équipes ayant un `team_country` non nul mais absent de `dim_countries` (code inconnu) tombent en repli textuel, ce qui peut donner un résultat incorrect si le nom de l'équipe contient le nom d'un autre pays.
    - `dim_teams` ne contient que les équipes ayant joué au moins un match à domicile ; les équipes uniquement extérieures sont absentes de ce modèle.
- **Validation** : À compléter par [Nom du validateur] et [Date].
