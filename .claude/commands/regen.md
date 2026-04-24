---
description: Regenerate dbt SQL models from .context.md source-of-truth files. Pass a model name to regenerate one, or nothing to regenerate all.
allowed-tools: Glob, Read, Write, Edit, Bash, Agent
---

Regenerate dbt SQL models from their `.context.md` context files.

**Arguments**: `$ARGUMENTS`

- Empty → regenerate ALL models in the project
- A model name (e.g. `stg_matches`) → regenerate that model only
- `--dry-run` → generate but do not write files (print to conversation only)

---

## Workflow

### 1. Identify models to process

If `$ARGUMENTS` contains a specific model name (not `--dry-run`):

- Target that single model.

Otherwise:

- Use Glob to find all `.context.md` files under `dbt_project/models/`:
  Pattern: `dbt_project/models/**/*.context.md`
- Extract the model name from each path (strip `.context.md` suffix).
- Skip `e2e_test_suite` (test context, not a model).

### 2. Regenerate each model

For each model, spawn a `sql-regenerator` agent:

```
Agent(
  subagent_type="sql-regenerator",
  description="Regenerate {model_name} from context",
  prompt="Regenerate the dbt model: {model_name}"
)
```

Spawn agents **in parallel** for independent models. Order of dependency:

- First pass (can run in parallel): `raw_*`, `stg_*`
- Second pass (can run in parallel): `dim_*`
- Third pass (can run in parallel): `fact_*`, `kpi_*`

Wait for each pass to complete before starting the next.

### 3. Merge schema snippets (unless --dry-run)

After all agents finish, check for any `*.schema.generated.yml` files created:

- For staging models: read `dbt_project/models/staging/schema.yml`
- For mart models: read `dbt_project/models/marts/schema.yml`

For each generated snippet:

- Read the snippet file
- Find the model's existing entry in `schema.yml` (search for `- name: {model_name}`)
- If found: replace it with the generated entry
- If not found: append it under the `models:` key
- Write back the updated `schema.yml`
- Delete the `.schema.generated.yml` snippet file

### 4. Validate (optional)

Ask the user: "Run `dbt run && dbt test` to validate the regenerated models?"

If yes:

```bash
cd "/Users/ippon/Documents/CODE/INTERCONTRAT/context platform/dbt project/dbt_project" && dbt run && dbt test 2>&1 | tail -30
```

### 5. Report

Produce a final summary table:

| Model | Status     | Bugs Fixed | Unresolved |
| ----- | ---------- | ---------- | ---------- |
| ...   | ✔ written | ...        | ...        |

Highlight any models with unresolved business rules that require human decisions before the model is correct.
