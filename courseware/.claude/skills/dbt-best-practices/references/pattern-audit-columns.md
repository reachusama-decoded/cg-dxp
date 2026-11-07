# Pattern: audit-columns

## Intent

Attach a standard set of **system-managed audit columns** to every curated table so that lineage, change tracking, and data quality investigations have a consistent set of system-populated fields to query. Column names are team-renameable via `.catalyst-build.yml#patterns.audit-columns`; the semantics are fixed.

## Required behavior

The audit column family covers three sub-groups:

1. **Row identity** — a surrogate key unique to the row version (see `pattern-surrogate-key.md`).
2. **Business time** — effective start/end dates for the row's business validity (`dl_business_start_date`, `dl_business_end_date`, `dl_current_indicator`).
3. **System time** — when the row was written to the data platform (`dl_system_start_timestamp`, `dl_system_end_timestamp`) and the source system identifier (`dl_record_source`, `dl_record_load_dttm`).

These columns are injected by calling the audit-column-injection macro (see `pattern-audit-column-injection.md`) rather than hand-authoring them in every model.

## Concrete implementations seen

- **Caspian (prototype):** `dl_` prefix family — `dl_row_uid`, `dl_business_start_date`, `dl_business_end_date`, `dl_current_indicator`, `dl_system_start_timestamp`, `dl_system_end_timestamp`, `dl_record_source`, `dl_record_load_dttm`. These are defined in the prototype's `macros/audit_columns.sql`.
- **Greenfield:** Rename prefix (e.g., `sys_`, `aud_`) by updating `.catalyst-build.yml#patterns.audit-columns.prefix`. All downstream skills read the prefix from the config, never hardcode `dl_`.

## Discovery

`/setup-dbt-project` scans `macros/` for a macro or variable set defining columns matching:
- a consistent prefix pattern (e.g., `dl_` or `sys_`)
- columns including a start date, end date, and current indicator

If found, extract the prefix and canonical column names into `.catalyst-build.yml#patterns.audit-columns`. If not found, default to `dl_` prefix and prompt the user to confirm or override.

## When skills use this

- `/source-aligned` (existing) injects `dl_record_load_dttm` and `dl_record_source` into staging models via the audit-column-injection macro.
- `/domain-aligned` injects the full `dl_*` bitemporal columns into dimension models using the bitemporal-incremental pattern.
- `pattern-audit-column-injection.md` defines the macro that performs the injection so models don't repeat column definitions.
- `schema.yml` descriptions for audit columns are standardized: `/setup-dbt-project` emits them automatically from a template.
