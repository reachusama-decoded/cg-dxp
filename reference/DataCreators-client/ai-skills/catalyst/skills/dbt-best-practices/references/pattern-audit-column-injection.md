# Pattern: audit-column-injection

## Intent

Centralize the **SELECT expressions** for the audit column family (see `pattern-audit-columns.md`) into a single macro so that every model gets the same column definitions without copy-paste. When the org renames or extends the audit column set, changing one macro updates all models.

## Required behavior

A macro that:

1. Returns a comma-separated list of SQL column expressions for the full audit column set (business time + system time + row identity).
2. Accepts optional arguments to control which sub-groups to include (e.g., `include_business_time=true`, `include_system_time=true`).
3. Reads column names from `.catalyst-build.yml#patterns.audit-columns` (via dbt vars) so the output uses team-configured names, not hardcoded `dl_*`.
4. Is invokable at the end of a SELECT: `SELECT t.*, {{ get_audit_cols() }}`.

## Concrete implementations seen

- **Caspian (prototype):** `get_audit_cols()` macro defined in `macros/audit_columns.sql`. Emits:
  ```sql
  CURRENT_TIMESTAMP() AS dl_record_load_dttm,
  '{{ var("record_source") }}'  AS dl_record_source,
  ...
  ```
  Called at the end of every staging and intermediate model's SELECT list.
- **Greenfield:** Rename to `<team_prefix>_get_audit_cols()`. Wire the `record_source` var in `dbt_project.yml` to the source system name for each schema.

## Discovery

`/setup-dbt-project` scans `macros/` for a macro whose name ends in `get_audit_cols` or `inject_audit_cols` (or contains both `audit` and `cols`/`columns`).

If found, store the macro name in `.catalyst-build.yml#patterns.audit-columns.injection_macro`. If not found, scaffold the macro from the Caspian template (with team-prefix rename) and add it to `macros/audit_columns.sql`.

## When skills use this

- `/source-aligned` (existing) appends `{{ get_audit_cols() }}` (team-renamed) to the SELECT of every staging model.
- `/domain-aligned` (existing) appends the macro for the system-time sub-group; the business-time columns come from the bitemporal-incremental strategy directly.
- `pattern-audit-columns.md` defines the semantics; this pattern defines the injection mechanism. The two patterns are always used together.
- `/setup-dbt-project` scaffolds `macros/audit_columns.sql` if not found, and adds `record_source` to `dbt_project.yml` vars.
