# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A dbt POC ("Context Platform") demonstrating a data pipeline for sports performance + population analytics. Stack: DuckDB (file-based at `dbt_project/dbt.duckdb`) + dbt 1.8+ + Evidence.dev dashboard. Documentation is in French.

## Commands

All dbt commands must run from `dbt_project/` (where `dbt_project.yml` lives):

```bash
cd dbt_project

dbt run                        # build all models
dbt test                       # run tests
dbt run && dbt test            # full pipeline
dbt run --select <model_name>  # single model
dbt test --select <model_name> # single model tests
dbt compile                    # compile without executing
dbt ls                         # list models
dbt snapshot                   # run all snapshots

# Snapshot comparison script (run from repo root)
python scripts/compare_snapshots_analysis.py
python scripts/compare_snapshots_analysis.py --output report.md --json
```

Dashboard (Evidence.dev):
```bash
npm --prefix ./dbt_project/reports run dev   # http://localhost:3000
```

Python env:
```bash
uv venv .venv && uv sync   # first-time setup
```

## Architecture

### Model Layers

```
data/*.parquet
  └── raw_*      (views)  — direct SELECT * from parquet files
      └── stg_*  (views)  — cleaned: renaming, type casts, filters
          └── dim_*  (tables) — dimensions (countries, teams, matches, population, team_country)
          └── fact_* (tables) — fact_country_performance
          └── kpi_*  (tables) — kpi_performance_vs_population
```

Snapshots in `dbt_project/snapshots/` use `check` strategy on all columns with `invalidate_hard_deletes=True`, targeting schema `snapshots`.

### Context Files (`.context.md`) — Source of Truth

Every model has a companion `.context.md` file (same directory). These are the **authoritative source** for what a model should do — the SQL is generated *from* them. Schema defined in `CONTEXT-SCHEMA.md`.

The `/regen` command regenerates SQL + `schema.yml` entries from `.context.md` files. **When editing model logic, edit the `.context.md` first**, then run `/regen <model_name>`.

Post-hook reminder: editing a `.context.md` triggers a hook that reminds you to run `/regen`.

### Known Business Bugs (already fixed in generated models)

These are documented in the `sql-regenerator` agent and must be preserved when regenerating:

1. **kpi_performance_vs_population**: join with `dim_population` must filter `WHERE p.year = 2023` and `p.population_value > 0` to avoid cartesian products and division by zero.
2. **fact_country_performance**: winner calculation must use `CASE WHEN f.winner = tc.team_name THEN 1` — counting away wins for home country was the original bug.
3. **dim_population / stg_indicators**: filter World Bank indicators to `indicator_code = 'SP.POP.TOTL'`.

### Governance Pattern: Early + Late Binding

- **Early Binding** — dbt contracts in `schema.yml` (enforced at compile/run time)
- **Late Binding** — `.context.md` files (human/AI-readable business context)

Together these form the "Context Platform" concept being demonstrated.

## Key Files

| File | Purpose |
|------|---------|
| `dbt_project/dbt_project.yml` | dbt config, materialization defaults |
| `profiles.yml` | DuckDB connection (`path: dbt.duckdb`, schema: `main`) |
| `CONTEXT-SCHEMA.md` | Standard schema for all `.context.md` files |
| `scripts/compare_snapshots_analysis.py` | Snapshot diff analysis utility |
| `.claude/settings.json` | Allowed dbt commands + context file hooks |
| `dbt_project/reports/` | Evidence.dev dashboard (Markdown pages) |

## Profiles

`profiles.yml` is at the repo root (not `~/.dbt/`). The `DBT_PROFILES_DIR` environment variable may need to point there if running dbt from outside `dbt_project/`:

```bash
export DBT_PROFILES_DIR=..  # relative to dbt_project/
```
