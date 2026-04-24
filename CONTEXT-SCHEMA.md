# Schéma de Documentation des Contextes Métier

## Vue d'ensemble

Les fichiers `.context.md` documentent le contexte métier et les spécifications techniques de chaque modèle dbt (données brutes, transformations intermédiaires et données finales). Ce schéma standardisé assure la cohérence et la complétude de la documentation à travers le projet.

## Structure standardisée

### 1. Titre

```markdown
# Contexte Métier — [nom_du_modele]
```

- Format : `# Contexte Métier — {nom_du_modèle}`
- Exemple : `# Contexte Métier — dim_population`

---

### 2. Section "Objectifs"

Définit clairement la raison d'être du modèle et son grain de détail.

```markdown
## Objectifs

- **Finalité** : [Description de l'objectif principal du modèle]
- **Grain** : [Clé/combinaison de clés identifiant une ligne unique]
```

**Règles** :

- La **Finalité** doit être concise (1-2 phrases max).
- Le **Grain** doit expliciter l'entité métier représentée par chaque ligne.
  - Exemples : "Une ligne par match unique", "Une ligne par combinaison **pays + année**", "Une ligne par équipe unique"

**Exemples** :

| Modèle                     | Finalité                                                                                                                                                            | Grain                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `dim_population`           | Fournir une table de population annuelle par pays (1960–2025) pour rapporter les performances sportives en fonction de la taille de la population.                  | Une ligne par combinaison **pays + année** |
| `stg_matches`              | Fournir une table brute de tous les matchs sportifs disponibles, servant de point d'entrée pour tous les traitements liés aux performances des équipes et des pays. | Une ligne par match unique                 |
| `fact_country_performance` | Fournir une table de faits mesurant les performances sportives agrégées par pays (matchs joués et victoires).                                                       | Une ligne par pays unique                  |

---

### 3. Section "Transformations"

Décrit la provenance des données, la logique métier appliquée et les exclusions.

```markdown
## Transformations

- **Source** : [Description de la/des table(s) source(s)]
- **Transformation** :
  - [Transformation 1]
  - [Transformation 2]
  - [Transformation n]
- **Exclusions** : [Données filtrées ou exclues, ou "Aucune exclusion"]
```

**Règles** :

- **Source** : Nommer la ou les table(s) source(s) d'où proviennent les données.
- **Transformation** : Lister les opérations métier appliquées (renommages, calculs, filtres, pivots, agrégations).
  - Pour les modèles bruts (staging), l'absence de transformation doit être explicite : "Aucune transformation majeure n'est effectuée à ce stade. Les données sont recopiées telles quelles."
  - Pour les modèles transformés, détailler chaque transformation de manière précise.
- **Exclusions** : Expliciter les données filtrées ou exclues (ex: NULL, zéros, doublons).

**Exemples** :

**Modèle de staging (brut)** :

```markdown
## Transformations

- **Source** : Fichier de référence externe contenant les noms de pays et leurs codes ISO.
- **Transformation** :
  - Aucune transformation majeure n'est effectuée.
  - Renommage simple : `Name` → `country_name`, `Code` → `code`.
- **Exclusions** : Aucune exclusion, toutes les lignes sources sont conservées.
```

**Modèle de marts complexe** :

```markdown
## Transformations

- **Source** : Données depuis `stg_matches` et `dim_team_country` (liaison équipe-pays).
- **Transformation** :
  - **Comptage des matchs joués** : Nombre de matchs où une équipe du pays était en domicile.
  - **Comptage des victoires** : Nombre de matchs domicile terminés avec victoire.
  - Agrégation par pays.
- **Exclusions** : Seuls les matchs à domicile sont comptabilisés. Les matchs en déplacement sont ignorés.
```

---

### 4. Section "Champs attendus"

Tableau détaillé de toutes les colonnes du modèle avec leurs caractéristiques.

```markdown
## Champs attendus

| Champ          | Format            | Nomenclature    | Règles/Tests         |
| -------------- | ----------------- | --------------- | -------------------- |
| [Nom du champ] | [Type de données] | `[nom_colonne]` | [Règles d'intégrité] |
```

**Structure du tableau** :

| Colonne          | Description                                                             | Exemple                                                   |
| ---------------- | ----------------------------------------------------------------------- | --------------------------------------------------------- |
| **Champ**        | Nom métier lisible du champ                                             | `Nom du pays`                                             |
| **Format**       | Type de données (Texte, Entier, Décimal, Date, DateTime, Booléen, JSON) | `Texte`, `Entier (bigint)`                                |
| **Nomenclature** | Nom exact de la colonne en minuscules avec underscores                  | `` `country_name` ``                                      |
| **Règles/Tests** | Contraintes d'intégrité et exigences de validation                      | `Obligatoire, non vide, unique`, `NULL si non disponible` |

**Règles de remplissage** :

1. **Champ** : Nom lisible, en français, décrivant le type de données.
2. **Format** : Type de données SQL standardisé. Ajouter des précisions si nécessaire.
   - `Texte`, `Entier`, `Bigint`, `Décimal`, `Date (YYYY-MM-DD)`, `DateTime`, `Booléen`, `JSON`, `Array`, etc.
3. **Nomenclature** : `snake_case` exact, entre backticks (` \`nom_colonne\` `).
4. **Règles/Tests** : Combiner les règles pertinentes :
   - Nullabilité : `Obligatoire` / `Optionnel`, `NULL possible`
   - Validations : `non vide`, `unique`, `valeur ≥ 0`, `doit être l'une de { valeur1, valeur2 }`
   - Provenance : `issu de ...`, `refère ...`
   - Restrictions logiques : `≤ [autre_champ]`

**Exemple concis** :

```markdown
| Nom du pays | Texte | `country_name` | Obligatoire, non vide |
| Année | Entier | `year` | Obligatoire, converté en entier (ex: "1960" → 1960) |
| Population | Bigint | `population_value` | Obligatoire, valeur brute (non arrondie), NULL si invalide |
```

---

### 5. Section "Tests de logique métier"

Décrit les tests de validation pour garantir l'intégrité des données.

```markdown
## Tests de logique métier

1. **Vérification du grain** :

   - [Assertion sur l'unicité et l'absence de doublons]
   - [Assertions sur la structure attendue]

2. **Validation des données** :

   - [Contraintes NOT NULL]
   - [Contraintes de format ou de valeur]
   - [Contraintes logiques inter-champs]

3. **Tests unitaires suggérés** :
   - [Test spécifique 1]
   - [Test spécifique 2]
   - [Test spécifique n]
```

**Trois niveaux de tests** :

#### 1.1 Vérification du grain

- Assurer que chaque ligne est unique selon la clé du grain.
- Vérifier l'absence de doublons.
- Affirmer que toutes les lignes ont une structure attendue (pas de ligne orpheline ou malformée).

**Exemple** :

```markdown
1. **Vérification du grain** :
   - Chaque pays doit apparaître une seule fois (unicité sur `country_name` et `code`).
   - Aucune ligne vide ou doublon autorisé.
```

#### 1.2 Validation des données

- Appliquer les contraintes NOT NULL, formats, valeurs valides.
- Vérifier les contraintes logiques entre champs (ex: `wins ≤ matches_played`).
- Confirmer les jointures avec tables de référence.

**Exemple** :

```markdown
2. **Validation des données** :
   - `match_id`, `home_team`, `away_team`, `home_score`, `away_score`, `winner` doivent être NOT NULL.
   - La valeur du champ `winner` doit être soit le nom d'une équipe (home_team ou away_team), soit "draw".
   - Si home_score > away_score, alors winner doit être home_team.
```

#### 1.3 Tests unitaires suggérés

- Proposer des tests spécifiques, concrets et vérifiables.
- Peut inclure : comparaisons avec un échantillon manuel, distribution statistique, vérification de jointures, détection de trous dans les données temporelles.

**Exemple** :

```markdown
3. **Tests unitaires suggérés** :
   - Vérifier l'absence de doublons sur `match_id`.
   - Valider que home_team ≠ away_team pour chaque ligne.
   - Compter le nombre de victoires, égalités et vérifier les proportions sont raisonnables.
   - Affirmer que le nombre de lignes en sortie = nombre de pays × nombre d'années avec données valides.
```

---

### 6. Section "Notes"

Synthèse des points importants, risques métier et responsabilités.

```markdown
## Notes

- **Incertitudes** :
  - [Risque ou ambiguïté 1]
  - [Risque ou ambiguïté 2]
  - [Risque ou ambiguïté n]
- **Validation** : À compléter par [Nom du validateur] et [Date].
```

**Structure** :

1. **Incertitudes** : Lister tous les risques métier, ambiguïtés techniques ou limitations connues du modèle.

   - Risques de données manquantes ou biaisées.
   - Hypothèses non validées.
   - Méthodes fragiles ou approximatives.
   - Limitations du champ d'application.
   - Couplages avec d'autres modèles.

2. **Validation** : Cadre de responsabilité pour la signature du document.
   - Format : "À compléter par [Nom du validateur] et [Date]."

**Exemple complet** :

```markdown
## Notes

- **Incertitudes** :
  - Les matchs à l'extérieur ne sont pas pris en compte, ce qui sous-estime le nombre réel de matchs joués et de victoires.
  - La correspondance équipe-pays est volontairement fragile (matching textuel). Les équipes dont le nom ne contient pas le pays seront perdues.
  - Le calcul des victoires pourrait être incorrect si les règles métier changent.
- **Validation** : À compléter par [Nom du validateur] et [Date].
```

---

## Emplacements des fichiers

Les fichiers de contexte sont organisés par couche de modèles :

```
dbt_project/
├── models/
│   ├── staging/
│   │   ├── raw_*.sql
│   │   ├── stg_*.sql
│   │   ├── stg_*.context.md        ← Contextes des modèles bruts
│   │   └── schema.yml
│   ├── marts/
│   │   ├── dim_*.sql
│   │   ├── fct_*.sql
│   │   ├── kpi_*.sql
│   │   ├── *.context.md             ← Contextes des modèles transformés
│   │   └── schema.yml
│   └── tests/
│       └── e2e/
│           └── e2e_test_suite.context.md  ← Contexte pour tests E2E
├── CONTEXT-SCHEMA.md                ← Ce fichier
└── ...
```

---

## Points clés à retenir

| Aspect                 | Directive                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Titre**              | Format unique : `# Contexte Métier — [nom_du_modèle]`                                                                  |
| **Ordre des sections** | Objectifs → Transformations → Champs attendus → Tests → Notes                                                          |
| **Clarté**             | Chaque section doit être comprise par un métier non-technique sans documentation externe.                              |
| **Complétude**         | Tous les champs et transformations doivent être documentés. Pas de détails omis.                                       |
| **Unicité**            | Chaque modèle a son propre fichier `.context.md` servant de source unique de vérité.                                   |
| **Maintenance**        | Mettre à jour le contexte **avant** de modifier la logique métier du modèle.                                           |
| **Mise à jour**        | Lorsque la logique métier change, commencer par mettre à jour `.context.md` et obtenir l'accord des parties prenantes. |

---

## Comment utiliser ce schéma

### Pour créer un nouveau fichier de contexte

1. Copier la structure ci-dessous dans un nouveau fichier `.context.md` :

   ```markdown
   # Contexte Métier — [nom_du_modèle]

   ## Objectifs

   - **Finalité** : [...]
   - **Grain** : [...]

   ## Transformations

   - **Source** : [...]
   - **Transformation** :
     - [...]
   - **Exclusions** : [...]

   ## Champs attendus

   | Champ | Format | Nomenclature | Règles/Tests |
   | ----- | ------ | ------------ | ------------ |

   ## Tests de logique métier

   1. **Vérification du grain** : [...]
   2. **Validation des données** : [...]
   3. **Tests unitaires suggérés** : [...]

   ## Notes

   - **Incertitudes** : [...]
   - **Validation** : À compléter par [Nom] et [Date].
   ```

2. Remplir chaque section en suivant les directives ci-dessus.

3. Faire relire et valider le contexte par les parties prenantes métier.

### Pour modifier un fichier existant

1. Identifier quelle section change (Transformations, Champs, Tests).
2. Proposer la modification au validateur métier.
3. Mettre à jour le fichier `.context.md` **avant** les changements de code dbt.
4. Mettre à jour la date de validation.

---

## Exemples de référence

Les fichiers suivants servent de modèles de référence :

- [dim_population.context.md](dbt_project/models/marts/dim_population.context.md) — Modèle complet avec pivot et transformations.
- [stg_matches.context.md](dbt_project/models/staging/stg_matches.context.md) — Modèle brut (aucune transformation).
- [fact_country_performance.context.md](dbt_project/models/marts/fact_country_performance.context.md) — Modèle agrégé avec jointures complexes.
