# Prepared dbt Model Generation Prompt

Generate a prepared/final dbt model with surrogate key and audit columns.

## Input

Read from source.yml:
- `columns`: All columns with surrogate_key flag
- `target_table`: Target table name
- `target_schema`: Target schema (default: cspn_fndn2)
- `dataset_type`: Master or Balance
- `load_type`: Full, balance, relationship, etc.
- `as_of_col`: Business date column (required for Balance)
- `domain`: Process domain

## Output Structure

```sql
{{
    config (
        schema = "{target_schema}_"|string + target.name,
        materialized = "incremental",
        incremental_strategy = "bitemporal_load_v2",
        load_type = "{load_type}",
        {partition_and_balance_config}
        file_format = "delta",
        unique_key = "dl_row_uid",
        meta = { "surrogate_key_cols": [{surrogate_keys}],
                 "audit_column_list": ["dl_last_update_process_id"]
                 {cluster_by_if_balance}
               },
        alias = '{target_table}',
        post_hook = ["vacuum {{ this }} retain 0 hours", "{{ cspn_commit_checkpoints() }}"]
    )
}}

{% set domain = config.model.meta.get("domain") -%}

SELECT
    {all_columns},
    {{ generate_surrogate_key_v3() }},
    dl_checksum_value, 
    {{ get_audit_cols() }},
    '{{ domain }}' as dl_source_system_code
FROM {{ ref("int_{target_table}") }}
```

## Config Variations by Dataset Type

### Master Dataset
```sql
load_type = "{load_type}",
partition_by = ["dl_current_indicator"],
```

### Balance Dataset
```sql
load_type = "balance",
as_of_col = "{as_of_col}",
detect_change_flag = "Y",
```

And in meta:
```sql
"cluster_by": ["dl_current_indicator", "{as_of_col}"]
```

## Surrogate Key Columns

Extract columns where `surrogate_key: Y` from source.yml and list them:
```sql
meta = { "surrogate_key_cols": ['col1', 'col2'], ... }
```

## Example Output - Master Dataset

```sql
{{
    config (
        schema = "cspn_fndn2_"|string + target.name,
        materialized = "incremental",
        incremental_strategy = "bitemporal_load_v2",
        load_type = "full",
        partition_by = ["dl_current_indicator"],
        file_format = "delta",
        unique_key = "dl_row_uid",
        meta = { "surrogate_key_cols": ['currencyuid'],
                 "audit_column_list": ["dl_last_update_process_id"]
               },
        alias = 'currency_evolve_v4',
        post_hook = ["vacuum {{ this }} retain 0 hours", "{{ cspn_commit_checkpoints() }}"]
    )
}}

{% set domain = config.model.meta.get("domain") -%}

SELECT
    currencyuid,
    isoalphathreecurrencycode,
    currencyname,
    effectivefromdate,
    effectivetodate,
    {{ generate_surrogate_key_v3() }},
    dl_checksum_value, 
    {{ get_audit_cols() }},
    '{{ domain }}' as dl_source_system_code
FROM {{ ref("int_currency_evolve_v4") }}
```

## Example Output - Balance Dataset

```sql
{{
    config (
        schema = "cspn_fndn2_"|string + target.name,
        materialized = "incremental",
        incremental_strategy = "bitemporal_load_v2",
        load_type = "balance",
        as_of_col = "period_end_date",
        detect_change_flag = "Y",
        file_format = "delta",
        unique_key = "dl_row_uid",
        meta = { "surrogate_key_cols": ['constituent_return_history_id'],
                 "audit_column_list": ["dl_last_update_process_id"],
                 "cluster_by": ["dl_current_indicator", "period_end_date"]
               },
        alias = 'constituent_return_history_v4',
        post_hook = ["vacuum {{ this }} retain 0 hours", "{{ cspn_commit_checkpoints() }}"]
    )
}}

{% set domain = config.model.meta.get("domain") -%}

SELECT
    constituent_return_history_id,
    index_family_code,
    period_start_date,
    period_end_date,
    total_return_usd_amount,
    {{ generate_surrogate_key_v3() }},
    dl_checksum_value, 
    {{ get_audit_cols() }},
    '{{ domain }}' as dl_source_system_code
FROM {{ ref("int_constituent_return_history_v4") }}
```

## File Naming

Save as: `models/prepared/{target_table}.sql`

Example: `models/prepared/currency_evolve_v4.sql`

## Validation

- All columns from source.yml are in SELECT
- Surrogate key columns match those with `surrogate_key: Y`
- Correct config for Master vs Balance
- as_of_col provided for Balance datasets
- References integration model correctly

## Incremental Strategies

The `templates/dbt_project/macros_overrides/cspn_strategy_overrides.sql`
file is vendored verbatim from
`cg-open-itg/edo-ig-data-products/shared/macros/spark_utils/` and ships
implementations of: `bitemporal_load_v2`, `scd2`, `match_merge`,
`match_merge_v2`, `upsert`, `delete_merge`.

- **`bitemporal_load_v2`** — production-validated. This is the default
  for prepared models in this skill; matches the working reference at
  `data_products/shared_ref/datasets/currency/dbt/prepared/currency.sql`
  in `edo-ig-data-products`. Uses the `dl_*` bi-temporal column family.
- **Other strategies** in the vendored file are available but
  **unvalidated** against the skill's emitted output. File a follow-up
  ticket with a smoke test if you need one.
- **dbt-native `snapshot`** is the standard SCD2 escape hatch. It uses
  dbt's `dbt_valid_*` column convention — a different column family
  from `dl_*` — so don't mix them in the same model.
