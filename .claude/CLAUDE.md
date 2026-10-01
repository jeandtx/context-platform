# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A dbt project on DuckDB (file-based at `dbt_project/dbt.duckdb`) with an Evidence.dev dashboard.

## Commands

All dbt commands must run from `dbt_project/` (where `dbt_project.yml` lives):

```bash
cd dbt_project

dbt run                        # build all models
dbt test                       # run tests
dbt compile                    # compile without executing
dbt ls                         # list models
dbt snapshot                   # run all snapshots
```

`profiles.yml` is at the repo root (not `~/.dbt/`). If running dbt from outside `dbt_project/`, set `DBT_PROFILES_DIR` accordingly.
