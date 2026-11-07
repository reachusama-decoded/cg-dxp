---
name: write-dbt-model
description: |
  Author a single dbt model `.sql` file under
  `{product}/dbt/{layer}/{model_name}.sql` plus update a per-layer
  `_{layer}__models.yml` config file with column test stubs. The rendered
  model is compliant with the SQL-DBSQL-* and PY-NAMING-* rules:
  snake_case model names, `file_format='delta'`, `location_root`
  (SQL-DBSQL-005 external tables), `VACUUM RETAIN 168 HOURS` hint
  (SQL-DBSQL-009), and merge-strategy incremental with `unique_key`
  (SQL-DBSQL-003).
  Trigger phrases: "write a dbt model", "scaffold a dbt model",
  "author dbt staging model", "create dbt model file".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies:
    - setup-dbt-project
  consumes:
    - data-contract
    - data-model
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - SQL-DBSQL-*
    - PY-NAMING-*
---

# write-dbt-model

Render a compliant dbt model file (plus per-layer yml stub) into a
data-product subtree.

## When to use

A domain team adds a new dbt model and needs the boilerplate scaffolded
against the Catalyst SQL-DBSQL-* rules without hand-rolling the config
block, location_root, vacuum hint, or yml test scaffolding.

## Inputs

CLI flags:

- `--product` (required) — path to `data-products/{domain}/datasets/{product}/`.
- `--model-name` (required) — snake_case.
- `--layer` (required) — one of `staging|intermediate|marts`.
- `--materialization` (required) — one of `table|view|incremental`.
- `--unique-key` (required when `--materialization=incremental`,
  SQL-DBSQL-003).

## Outputs

- `<product>/dbt/<layer>/<model_name>.sql` — rendered model.
- `<product>/dbt/<layer>/_<layer>__models.yml` — created or updated
  with the model's column test stubs.

## Standards

- `SQL-DBSQL-003` — incremental models use `incremental_strategy='merge'`
  with `unique_key`.
- `SQL-DBSQL-005` — `location_root` config rendered for table/incremental
  materializations (external table requirement).
- `SQL-DBSQL-009` — `VACUUM RETAIN 168 HOURS` hint in the model file.
- `PY-NAMING-*` — snake_case model names enforced; non-conforming names
  exit 2.

## Loaded by

- `authoring-dbt-on-dbsql` — document-tier reasoning and worked examples.

## Procedure

1. Validate `--model-name` is snake_case → exit 2 otherwise.
2. Validate `--materialization=incremental` implies `--unique-key`.
3. Render the appropriate template (`model.sql.tmpl` or
   `model_incremental.sql.tmpl`) with `<<VAR>>` substitution.
4. Render or merge `_<layer>__models.yml` with a column-test stub.
5. Write both files; print the paths and the rule IDs satisfied.

## Failure modes

- Non-snake_case `--model-name` → exit 2.
- `--materialization=incremental` without `--unique-key` → exit 2.
- Unknown `--layer` or `--materialization` → argparse rejects (exit 2).
- Existing model file at the target path → overwritten silently. The yml
  is merged (the model entry is replaced; other models preserved).
