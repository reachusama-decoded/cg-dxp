# Pattern: bitemporal-incremental

## Intent

Load slowly-changing dimension data incrementally using a **bitemporal** strategy: track both the business validity period (`dl_business_start_date` / `dl_business_end_date`) and the system record period (`dl_system_start_timestamp` / `dl_system_end_timestamp`) so that point-in-time queries can reconstruct state as of either axis independently.

This is an SCD Type 2 variant designed for Databricks Delta MERGE — avoids full-refresh costs on large tables while maintaining complete change history.

## Required behavior

A macro or materialization strategy that:

1. Accepts a `unique_key` (business key columns, list or string) and a `updated_at` / `record_load_dttm` watermark column.
2. On incremental run: issues a Delta MERGE that:
   - Closes existing open rows for matched business keys (sets `dl_business_end_date` / `dl_current_indicator = false`).
   - Inserts new rows for changed records with `dl_business_start_date = <source_effective_date>` and `dl_current_indicator = true`.
3. Works correctly on `--full-refresh` (drops and recreates; no orphaned open rows).
4. Emits RFD 0008 `SQL-INCR-002` compliant `merge` strategy on Databricks.

## Concrete implementations seen

- **Caspian (prototype):** `bitemporal_load_v2` — a custom dbt materialization registered in `macros/materializations/`. Called via `{{ config(materialized='bitemporal_load_v2', unique_key=['<bk_col>'], ...) }}`. Internally issues a 2-step MERGE + INSERT.
- **Greenfield (recommended):** Use the `bitemporal_load_v2` pattern shape; rename to `<team_prefix>_bitemporal_load`. The macro signature and MERGE logic are the authoritative contract — the name is team-renameable.

## Discovery

`/setup-dbt-project` scans `macros/materializations/` for a file defining a custom materialization that:
- mentions `merge` + `business_start` (or `dl_business_start`) in its body
- has an `incremental_strategy`-like argument

If found, store the macro name in `.catalyst-build.yml#patterns.incremental-bitemporal.strategy`. If not found and the project has SCD2-shaped models, prompt the user.

## When skills use this

- `/domain-aligned` (existing) emits `{{ config(materialized=patterns.incremental-bitemporal.strategy, unique_key=[...]) }}` for dimension models where the data-model.md specifies SCD Type 2 or bitemporal history.
- `/dbt-best-practices` references this pattern when a user asks "how do I track history for a dimension" or "SCD2 on Databricks."
- Rule `SQL-INCR-002` (merge strategy required on Databricks) is enforced here — this pattern satisfies it.
