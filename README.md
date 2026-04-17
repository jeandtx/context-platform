# Plateforme de Contexte — Projet dbt

## 🎯 Vue d'ensemble

Ce projet démontre un pipeline de données complet :

```
Données brutes (CSV) → DuckDB → Modèles dbt → Analyses finales
```

Le projet inclut :

- Données clients et transactionnelles de démonstration
- Modèles dbt pour la représentation intermédiaire et la transformation
- Tests de qualité des données (unicité, contraintes NOT NULL)
- Documentation métier complète via les fichiers `.context.md`

## 📋 Prérequis

- Python 3.10+
- pip (gestionnaire de paquets Python)
- Git

## 🚀 Démarrage rapide

### 1. Configuration de l'environnement

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project"
uv venv .venv
source .venv/bin/activate
```

### 2. Installation des dépendances

```bash
uv sync
```

### 3. Construire les modèles dbt

```bash
cd dbt_project
export DBT_PROFILES_DIR=../.dbt
dbt run      # Construire tous les modèles
dbt test     # Exécuter les tests de qualité des données
```

### 4. Démarrer Evidence.dev

```bash
npm --prefix ./reports run dev
```

Ouvrir http://localhost:3000 dans le navigateur pour voir le tableau de bord.

## 📁 Structure du projet

```
.
├── README.md                          # Ce fichier
├── pyproject.toml                     # Dépendances Python
├── dbt.duckdb                         # Fichier base de données DuckDB (créé automatiquement)
│
├── .dbt/
│   └── profiles.yml                   # Configuration du profil dbt pour DuckDB
│
├── CONTEXT-SCHEMA.md                  # Schéma de documentation des modèles
│
└── dbt_project/                       # Racine du projet dbt
    ├── dbt_project.yml                # Configuration du projet dbt
    ├── models/
    │   ├── schema.yml                 # Définitions des modèles et tests
    │   ├── staging/
    │   │   ├── raw_*.sql              # Données brutes (sources)
    │   │   ├── stg_*.sql              # Transformations de représentation intermédiaire
    │   │   └── *.context.md           # Contextes métier des modèles de staging
    │   └── marts/
    │       ├── dim_*.sql              # Tables de dimension
    │       ├── fct_*.sql              # Tables de faits
    │       ├── kpi_*.sql              # Indicateurs clés de performance
    │       └── *.context.md           # Contextes métier des modèles de marts
    ├── tests/
    │   └── e2e_test_suite.context.md  # Documentation des tests E2E
    ├── logs/
    │   └── query_log.sql              # Journal des requêtes exécutées
    ├── reports/                       # Tableau de bord Evidence.dev
    │   ├── evidence.config.yaml       # Configuration Evidence
    │   ├── package.json               # Dépendances Node.js
    │   ├── pages/                     # Pages du tableau de bord
    │   │   └── *.md
    │   └── sources/                   # Sources de données
    │       ├── dbt.duckdb             # Base de données DuckDB
    │       └── *.sql
    └── target/                        # Modèles compilés (généré automatiquement)
```

## � Early Binding vs Late Binding

### Concept: Deux Approches Complémentaires pour Documenter et Valider les Données

Ce projet démontre une approche hybride de gestion des données qui combine deux stratégies de liaison (binding) des données et de leurs contextes :

#### 📋 **Early Binding (Contrats dbt)**

**Définition** : Liaison précoce des contraintes de données au moment de la _compilation_ et de l'_exécution_ du pipeline dbt.

**Emplacement** : `dbt_project/models/*/schema.yml`

**Caractéristiques** :

- ✅ **Enforced à la compilation** : Les contraintes sont vérifiées dès le lancement de `dbt run` et `dbt test`
- ✅ **Précises et mesurables** : Définissent exactement quelles colonnes doivent exister, leurs types et leurs validations
- ✅ **Exécutées automatiquement** : Les tests dbt (NOT NULL, UNIQUE, accepted_values, etc.) s'exécutent à chaque build
- ⚠️ **Limités en contexte métier** : Décrivent le _quoi_ et le _comment_, pas le _pourquoi_

**Commande** : `dbt test` valide tous les contrats définis.

---

#### 📖 **Late Binding (Context Store)**

**Définition** : Liaison tardive du contexte métier et des spécifications détaillées, documentées _indépendamment_ du pipeline technique.

**Emplacement** : `dbt_project/models/*/[model_name].context.md`

**Caractéristiques** :

- 📝 **Documenté, non exécuté** : Le contexte métier est stocké et documenté mais non validé automatiquement
- 📊 **Holistique** : Capture la finalité métier, le grain, les transformations, les exclusions et les risques
- 🔍 **Human-readable** : Destiné à être lu et compris par les métiers et les analystes
- 🤝 **Source unique de vérité** : Définit l'accord entre technologie et métier

---

### 🔄 Complémentarité : Comment Elles Fonctionnent Ensemble

| Dimension      | Early Binding (Contrats dbt)        | Late Binding (Context Store)                                             |
| -------------- | ----------------------------------- | ------------------------------------------------------------------------ |
| **Quand**      | À la compilation / exécution        | Avant et après le développement                                          |
| **Qui**        | Exécuté par dbt automatiquement     | Lu par les humains, les métiers et les validateurs                       |
| **Portée**     | Technique : structure et tests      | Métier : intentions, transformations, risques                            |
| **Validation** | ✅ Automatisée                      | 📋 Manuelle (signature de validation)                                    |
| **Exemple**    | NOT NULL, UNIQUE, types de colonnes | Objectif = "identifier uniformément les pays", Grain = "par pays unique" |
| **Réactivité** | Rapide (complet à chaque run)       | Lent (dépend des revues métier)                                          |

### 📚 Workflow Recommandé

1️⃣ **Définir d'abord le contexte métier** → `.context.md`

- Décrire l'objectif, le grain, les transformations
- Obtenir l'accord des parties prenantes métier

2️⃣ **Traduire en contrats techniques** → `schema.yml`

- Ajouter les tests dbt qui valident le contexte
- Implémenter les colonnes et les validations

3️⃣ **Valider par exécution** → `dbt run && dbt test`

- Les Early Binding (contrats) vérifient la qualité technique

4️⃣ **Maintenir la cohérence** → Mettre à jour les deux si le modèle change

---

## 📊 Evidence.dev

### Démarrer le tableau de bord

```bash
npm --prefix ./reports run dev
```

Le tableau de bord est accessible à http://localhost:3000

## � Configuration

### Configuration dbt (`.dbt/profiles.yml`)

```yaml
dbt_poc:
    target: dev
    outputs:
        dev:
            type: duckdb
            path: "dbt.duckdb"
            schema: "main"
            threads: 4
```

## 📝 Documentation

### Schéma de contexte

Consultez `CONTEXT-SCHEMA.md` pour comprendre la structure standardisée des fichiers `.context.md`.

### Fichiers de contexte métier

Chaque modèle dbt possède un fichier `.context.md` correspondant documentant :

- **Objectifs** : Finalité et grain du modèle
- **Transformations** : Source, logique appliquée, exclusions
- **Champs attendus** : Catalogue des colonnes avec types et règles
- **Tests de logique métier** : Validations et assertions
- **Notes** : Incertitudes et signatures des validateurs
