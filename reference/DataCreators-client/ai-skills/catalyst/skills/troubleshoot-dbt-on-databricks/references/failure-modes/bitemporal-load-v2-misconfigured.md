# Materialization Fails — bitemporal_load_v2 Misconfigured — Full Fix

## Symptoms to grep for

```
macro 'bitemporal_load_v2' not found
'bitemporal_load_v2' is undefined
missing required config attribute
KeyError: 'effective_from_column'
KeyError: 'primary_key'
dbt.exceptions.CompilationError
```

## Root cause

The `bitemporal_load_v2` custom materialization macro is not part of the
standard dbt distribution — it is a Capital Group internal macro. It must
be present in the project's `macros/` directory and included in the bundle's
upload manifest.

## Diagnostic steps — macro not found

1. Check that `macros/bitemporal_load_v2.sql` exists in the dbt project:
   ```bash
   ls macros/bitemporal_load_v2.sql
   ```
2. If missing, copy from the shared macro library (ask the platform team for
   the canonical source).
3. Confirm `databricks.yml` includes the macros directory in its `include`
   list:
   ```yaml
   bundle:
     name: dbt-employee-pipeline
   include:
     - models/
     - macros/
     - dbt_project.yml
     - profiles.yml
     - dbt_wrapper.py
   ```

## Diagnostic steps — missing config attribute

1. Compare the `{{ config(...) }}` block in the failing model against the
   required keys for `bitemporal_load_v2`.

Required config keys for `bitemporal_load_v2` (minimum):

```sql
{{ config(
    materialized='bitemporal_load_v2',
    primary_key=['employee_id'],
    effective_from_column='effective_from',
    effective_to_column='effective_to',
    is_current_column='is_current',
    incremental_strategy='merge'
) }}
```

2. Add any missing keys to the model's `{{ config(...) }}` block.
3. Run `dbt compile --target local --select <model>` to validate the config
   resolves without errors before re-deploying.
