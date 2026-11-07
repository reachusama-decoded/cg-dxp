# dbt Schema YAML Generation — Domain-Aligned

Generate `schema.yml` for the domain-aligned dbt project.

## Structure

```yaml
version: 2

sources:
  - name: <source_group_name>
    database: "{{ env_var('DATABRICKS_DEFAULT_CATALOG') }}"
    schema: "{{ env_var('DATABRICKS_DEFAULT_SCHEMA') }}"
    tables:
      - name: <source_table_1>
        description: "<vendor1> source table for <entity>"
      - name: <source_table_2>
        description: "<vendor2> source table for <entity>"

models:
  - name: stg_<vendor1>_<entity>
    description: "Staging model — standardizes <vendor1> <entity> columns to canonical schema"
    columns:
      - name: <canonical_key_col>
        description: "Natural key — <description>"
        tests:
          - not_null

  - name: stg_<vendor2>_<entity>
    description: "Staging model — standardizes <vendor2> <entity> columns to canonical schema"
    columns:
      - name: <canonical_key_col>
        description: "Natural key — <description>"
        tests:
          - not_null

  - name: int_<model>_union
    description: "Intermediate model — UNION ALL of staging models for <model>"

  - name: <model>
    description: "Canonical <entity> model — domain-aligned, bi-temporal"
    columns:
      - name: dl_row_uid
        description: "Surrogate key (MD5 of natural key columns)"
        tests:
          - not_null
          - unique
      - name: <canonical_key_col>
        description: "<description>"
        tests:
          - not_null
      - name: dl_source
        description: "Source vendor/system identifier"
        tests:
          - not_null
      - name: dl_business_from_date
        description: "Business validity start date"
        tests:
          - not_null
      - name: is_current
        description: "TRUE if this is the latest version for this key"
        tests:
          - not_null
      # Add all business columns from model spec
```

## Rules

1. **Sources section:** Define one source entry per UC table used by staging models
2. **Database/schema:** Always use `env_var()` — never hardcode catalog or schema names
3. **Tests on canonical model:**
   - `not_null` + `unique` on `dl_row_uid`
   - `not_null` on all natural key columns
   - `not_null` on `dl_source`, `dl_business_from_date`, `is_current`
4. **Column descriptions:** Pull from the model spec YAML
5. **Staging models:** At minimum, `not_null` on the natural key column
6. **Intermediate model:** No tests needed (it's a pass-through UNION)
