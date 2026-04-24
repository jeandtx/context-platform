# Contexte Métier — fact_country_performance

## Objectifs

- **Finalité** : Fournir une table de faits mesurant les performances sportives agrégées par pays (matchs joués et victoires).
- **Grain** : Une ligne par pays unique.

## Transformations

- **Source** : Données depuis `dim_matches` et `dim_team_country` (liaison équipe-pays).
- **Transformation** :
  - **Comptage des matchs joués** : Nombre de matchs où une équipe du pays était en domicile.
  - **Comptage des victoires** : Nombre de matchs domicile terminés avec victoire (winner = nom de l'équipe, à vérifier).
  - Agrégation par pays.
- **Exclusions** : Seuls les matchs à domicile sont comptabilisés. Les matchs en déplacement sont ignorés.

## Champs attendus

| Champ               | Format | Nomenclature     | Règles/Tests                                        |
| ------------------- | ------ | ---------------- | --------------------------------------------------- |
| Nom du pays         | Texte  | `country_name`   | Obligatoire, non vide, issu de `dim_team_country`   |
| Matchs joués (dom.) | Entier | `matches_played` | Obligatoire, valeur ≥ 0 (nombre de matchs domicile) |
| Victoires (dom.)    | Entier | `wins`           | Obligatoire, valeur ≥ 0, ≤ matches_played           |

## Tests de logique métier

1. **Vérification du grain** :
   - Chaque pays doit apparaître une seule fois (unicité sur `country_name`).
   - Aucune ligne vide ou doublon autorisé.
2. **Validation des données** :
   - `country_name`, `matches_played`, `wins` doivent être NOT NULL.
   - Les valeurs doivent être des entiers positifs ou zéro.
   - La contrainte logique `wins ≤ matches_played` doit toujours être vérifiée.
3. **Tests unitaires suggérés** :
   - Vérifier que `wins` ≤ `matches_played` pour chaque ligne.
   - Valider le comptage sur un échantillon manuel de pays.
   - Vérifier le nombre total de matchs comptés correspond à la source.
   - S'assurer que la liaison avec `dim_team_country` n'omet pas de pays.

## Notes

- **Incertitudes** :
  - **Les matchs à l'extérieur ne sont pas pris en compte**, ce qui sous-estime le nombre réel de matchs joués et de victoires pour chaque pays.
  - **Le calcul des victoires pourrait être incorrect** : comment est déterminé le vainqueur si un match est nul (draw) ? La logique doit être clarifiée avec la table `dim_matches`.
  - Si la correspondance équipe-pays est imparfaite (voir `dim_team_country`), certains pays peuvent être absents ou mal comptabilisés.
  - Les pays sans matchs domicile n'apparaissent pas dans cette table.
- **Validation** : À compléter par [Nom du validateur] et [Date].
