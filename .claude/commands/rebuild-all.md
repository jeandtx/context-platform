---
description: Full rebuild from context files — discovers lineage, generates SQL model by model in dependency order (dbt run after each), merges schema.yml, then compiles, runs, and tests everything.
allowed-tools: Glob, Read, Write, Edit, Bash, Agent
---

Full pipeline rebuild from `.context.md` source-of-truth files.

---

## Phase 1 — Discover context files

Glob all context files:

```
dbt_project/models/**/*.context.md
```

Collect the list. Exclude `e2e_test_suite` (not a model).

For each file, note:

- **model name** — filename without `.context.md`
- **layer** — `staging` if `raw_*` or `stg_*`, otherwise `marts`

---

## Phase 2 — Build lineage

For each context file, read it and extract **upstream model references**: scan for any token matching `raw_\w+`, `stg_\w+`, `dim_\w+`, `fact_\w+`, `kpi_\w+` in the Transformations / Sources section that is _not_ the model itself.

Build a dependency graph: `model → [upstream models it depends on]`.

Perform a **topological sort** to get ordered waves (models in the same wave have no inter-dependencies and can run in parallel):

- **Wave 0** — models with no upstream dbt models (typically `raw_*`)
- **Wave 1** — models whose all upstreams are in wave 0 (typically `stg_*`)
- **Wave 2** — models whose all upstreams are in waves 0–1 (typically `dim_*`)
- **Wave 3** — models whose all upstreams are in waves 0–2 (typically `fact_*`)
- **Wave 4+** — remaining models (typically `kpi_*`)

Print the resolved wave plan before proceeding, e.g.:

```
Wave 0: raw_matches, raw_events, raw_indicators, raw_country_codes
Wave 1: stg_matches, stg_events, stg_indicators, stg_country_codes
Wave 2: dim_teams, dim_countries, dim_matches, dim_population, dim_team_country
Wave 3: fact_country_performance
Wave 4: kpi_performance_vs_population
```

---

## Phase 3 — Generate SQL + immediate dbt run, wave by wave

Process each wave in order. Within a wave, spawn all `sql-regenerator` agents **in parallel**, then wait for the entire wave to finish before proceeding.

For each model in the wave:

```
Agent(
  subagent_type="sql-regenerator",
  description="Regenerate {model_name} from context",
  prompt="Regenerate the dbt model: {model_name}"
)
```

After all agents in a wave complete:

### Merge schema snippets for the wave

For each model in the wave that produced a `*.schema.generated.yml`:

1. Determine the target schema file:
   - `raw_*` / `stg_*` → `dbt_project/models/staging/schema.yml`
   - everything else → `dbt_project/models/marts/schema.yml`
2. Read the target `schema.yml`
3. Find the model's existing entry (`- name: {model_name}`) and replace it, or append under `models:` if absent
4. Write the updated `schema.yml`
5. Delete the `.schema.generated.yml` snippet

### Run the wave

After merging all schema snippets for the wave, run all models in the wave at once:

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && dbt run --select {model1} {model2} ... 2>&1 | tail -40
```

If `dbt run` fails for any model in the wave:

- Show the error output
- Attempt to diagnose (read the generated SQL for the failing model)
- Apply a fix directly to the SQL file
- Retry `dbt run --select {failing_model}` once
- If it still fails, **stop** and report: list which models succeeded and which failed, with the error. Do not proceed to later waves.

Repeat Phase 3 for every wave until all waves are processed.

---

## Phase 4 — Generate documentation and tests (schema.yml review)

After all waves complete, do a final pass over both `schema.yml` files:

1. Read `dbt_project/models/staging/schema.yml`
2. Read `dbt_project/models/marts/schema.yml`
3. For each model entry, verify it has:
   - A meaningful `description` (not blank)
   - `columns:` entries for every column produced by the model (cross-check against the generated SQL SELECT list)
   - Appropriate `tests:` — at minimum `not_null` on the grain columns, `unique` on primary keys, `accepted_values` where an enum is documented in the context file
4. Fill in any gaps directly by editing the `schema.yml` files

---

## Phase 5 — dbt compile and full run

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && dbt compile 2>&1 | tail -20
```

If compile succeeds:

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && dbt run 2>&1 | tail -40
```

If either command fails, diagnose the error (read the compiled SQL in `target/compiled/`), fix the source model SQL, and retry.

---

## Phase 6 — dbt test all

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && dbt test 2>&1 | tail -50
```

If any tests fail:

- Identify whether it is a **data quality issue** (the data genuinely violates the rule) or a **test definition issue** (the constraint in `schema.yml` is wrong)
- For test definition issues: fix `schema.yml` and rerun `dbt test --select {model}`
- For data quality issues: report them clearly but do not silently remove the test — surface them to the user

---

## Final report

Produce a summary table:

| Wave | Model       | SQL        | dbt run | Tests |
| ---- | ----------- | ---------- | ------- | ----- |
| 0    | raw_matches | ✔ written | ✔      | —     |
| ...  |             |            |         |       |

Then list:

- **Bugs fixed** (from sql-regenerator)
- **Test failures** that are data quality issues (need human review)
- **Any unresolved ambiguities** from context files
