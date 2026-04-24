---
description: Translate a natural language question into a DuckDB SQL query against the dbt mart models, then optionally execute it.
allowed-tools: Glob, Read, Bash
---

Translate the following question into a DuckDB SQL query and optionally run it.

**Question**: `$ARGUMENTS`

---

## Workflow

### Step 1 — Load the data model

Read both schema files to know every available table and column:

- `dbt_project/models/marts/schema.yml` — dims, facts, KPIs (these are materialised as **tables** in DuckDB)
- `dbt_project/models/staging/schema.yml` — staging views (available but prefer marts for analytics)

Also read any `.context.md` files that seem relevant to the question (glob `dbt_project/models/**/*.context.md` and pick the most relevant ones based on the question keywords).

### Step 2 — Identify relevant tables

Based on the question, decide which tables to use. Prefer the marts layer:

| Table                           | Contains                                                                           |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `dim_countries`                 | country_name, iso2                                                                 |
| `dim_teams`                     | team_id, team_name, team_gender, team_country                                      |
| `dim_matches`                   | match_id, match_date, home_team, away_team, home_score, away_score, winner         |
| `dim_population`                | country_name, country_code, indicator_name, indicator_code, year, population_value |
| `dim_team_country`              | team_name, country_name                                                            |
| `fact_country_performance`      | country_name, matches_played, wins                                                 |
| `kpi_performance_vs_population` | country_name, wins, population_value, performance_ratio                            |

Staging views are in the same DuckDB schema (`main`) as the marts tables.

### Step 3 — Generate the SQL

Write a DuckDB-compatible SQL query that answers the question. Rules:

- Use plain table names (no `ref()` — this is direct DuckDB, not dbt)
- All tables are in schema `main`; unqualified names work fine
- Prefer marts tables over staging views
- Add `LIMIT 20` to broad SELECT queries unless the question requires a full result set
- Use DuckDB idioms: `::type` for casts, `epoch_ms()` / `strftime()` for dates, window functions where helpful
- If the question is ambiguous, pick the most reasonable interpretation and note it

### Step 4 — Present the query

Show the generated SQL in a fenced code block with the `sql` language tag.

Briefly explain (1–2 sentences) what the query does and any assumption you made.

### Step 5 — Offer to execute

Ask: "Run this query against `dbt.duckdb`?"

If the user says yes (or if they confirmed as part of the original request), execute:

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && duckdb dbt.duckdb "<query>"
```

Replace `<query>` with the generated SQL, collapsing it to a single line (escape inner double-quotes as `\"`).

Display the results as a markdown table if the output is tabular. If the query fails, diagnose the error, fix the SQL, and retry once.
