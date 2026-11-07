# Pattern: checkpoint-table

## Intent

Persist the **high-water-mark** of each incremental load to a Delta checkpoint table so that restarts, retries, and partial-failure scenarios can resume from the last committed position rather than re-processing from the beginning or doing a full-refresh.

This decouples the incremental filter (`WHERE updated_at > <last_checkpoint>`) from the dbt model's own run metadata — the checkpoint survives warehouse restarts, dbt state loss, and CI re-runs.

## Required behavior

A macro (used as a `post_hook`) that:

1. Accepts a table reference (or var name pointing to the checkpoint table) and the current high-water-mark value (e.g., `max(updated_at)` computed in the model).
2. On successful model completion: UPSERTs one row to the checkpoint table keyed by `model_name` (or a caller-specified key), setting `last_committed_ts` / `last_committed_date`.
3. A companion read macro (or a `{{ var('checkpoint_table') }}` reference in the model's WHERE clause) lets the model read back the most-recent checkpoint at the start of the next run.

If the model fails mid-run, the checkpoint is NOT updated (post_hook only runs on success).

## Concrete implementations seen

- **Caspian (prototype):** `cspn_commit_checkpoints()` post_hook. Called in model `{{ config(..., post_hook=["{{ cspn_commit_checkpoints(this, max_ts) }}"]) }}`. Reads back via `{{ var('checkpoint_table') }}` in the incremental filter.
- **Greenfield:** Rename to `<team_prefix>_commit_checkpoints`. The checkpoint table name is injected via `var('checkpoint_table')` (team sets this in `dbt_project.yml` vars or `profiles.yml`).

## Discovery

`/setup-dbt-project` scans model configs and `dbt_project.yml` for:
- `post_hook` referencing a macro whose name contains `checkpoint` or `commit`
- a `var('checkpoint_table')` or similar

If found, record the macro name in `.catalyst-build.yml#patterns.checkpoint.commit_macro` and the var name in `.catalyst-build.yml#patterns.checkpoint.table_var`. If not found, warn the user that incremental models have no durable checkpoint and offer to scaffold one.

## When skills use this

- `/domain-aligned` (existing) emits the `post_hook` call when authoring incremental dimension models (bitemporal or otherwise).
- `/source-aligned` emits the checkpoint pattern for high-volume staging incremental models where offset tracking is needed.
- `/setup-dbt-project` provisions the checkpoint table DDL (a simple Delta table with `model_name STRING, last_committed_ts TIMESTAMP`) as part of the initial scaffold.
