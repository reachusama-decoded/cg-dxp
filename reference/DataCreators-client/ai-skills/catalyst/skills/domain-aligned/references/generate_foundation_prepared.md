# Generate Foundation Prepared Model (Domain-Aligned)

Create the prepared SQL model that applies the bitemporal incremental strategy,
generates a surrogate key, adds audit columns, and references the integration
UNION model.

## Key Difference from Single-Source (entity-scaffold)

The prepared model references `int_<entity_name>_union` (with `_union` suffix)
instead of `int_<entity_name>`. The prepared layer itself is identical in
structure -- the multi-source consolidation is handled entirely in the
integration layer.

## Template -- Balance with bitemporal_load_v2

```sql
{{
        config (
                schema = "<prepared_schema>"|string + target.name,
                materialized = "incremental",
                incremental_strategy = "bitemporal_load_v2",
                load_type = 'balance',
                as_of_col = "<as_of_col>",
                file_format = "delta",
                detect_change_flag = 'Y',
                unique_key = "dl_row_uid",
                meta = { "audit_column_list" :  ["dl_last_update_process_id"],
                         "surrogate_key_cols" : <pk_columns_list>
                        },
                post_hook = ["vacuum {{ this }} retain 0 hours",
                             "{{ cspn_commit_checkpoints() }}"]
        )
}}

{% set domain = config.model.meta.get('domain') -%}

SELECT
  <business_column_list>,
  dl_source,
  {{ generate_surrogate_key_v3() }},
  dl_checksum_value,
  {{get_audit_cols()}},
  '{{domain}}' AS dl_source_system_code
FROM {{ref("int_<entity_name>_union")}}
```

## Template -- Master (no as_of_col)

For master datasets, the config is similar but `load_type` is `'full'` and
`as_of_col` is omitted:

```sql
{{
        config (
                schema = "<prepared_schema>"|string + target.name,
                materialized = "incremental",
                incremental_strategy = "bitemporal_load_v2",
                load_type = 'full',
                file_format = "delta",
                detect_change_flag = 'Y',
                unique_key = "dl_row_uid",
                meta = { "audit_column_list" :  ["dl_last_update_process_id"],
                         "surrogate_key_cols" : <pk_columns_list>
                        },
                post_hook = ["vacuum {{ this }} retain 0 hours",
                             "{{ cspn_commit_checkpoints() }}"]
        )
}}

{% set domain = config.model.meta.get('domain') -%}

SELECT
  <business_column_list>,
  dl_source,
  {{ generate_surrogate_key_v3() }},
  dl_checksum_value,
  {{get_audit_cols()}},
  '{{domain}}' AS dl_source_system_code
FROM {{ref("int_<entity_name>_union")}}
```

## Key Rules

### dl_source Column

- Include `dl_source` in the business column list of the prepared model.
- This column tracks which vendor/source provided the row and is valuable
  for downstream consumers.
- It is passed through from staging --> integration --> prepared.

### Schema Prefix

- **IM:** `cspn_fndn2_` (foundation schema).
- **MSS:** `cspn_fndn2_` for most entities; `cspn_cons2_` for consolidated
  entities. Check existing prepared models in the same dc_tag to confirm.

### Surrogate Key

- `{{ generate_surrogate_key_v3() }}` reads PK columns from
  `meta.surrogate_key_cols` in the config block.
- The PK columns must be listed as a Python list of strings.
- Example: `['security_uid', 'as_of_date']`.
- Do NOT include `dl_source` in the surrogate key unless the same natural key
  legitimately appears from different sources and both rows should be retained.

### Audit Columns

- `{{ get_audit_cols() }}` generates standard audit columns:
  `dl_last_update_process_id`, plus any others listed in
  `meta.audit_column_list`.

### Domain

- `{% set domain = config.model.meta.get('domain') -%}` reads the domain
  from the model YAML meta block.
- Produces `dl_source_system_code` column with the domain value.
- For multi-source models, use the **primary domain** (the most authoritative
  source system).

### Post Hook

- `vacuum {{ this }} retain 0 hours` -- compact Delta table.
- `{{ cspn_commit_checkpoints() }}` -- commit checkpoints for recovery.
- Both are standard and should always be included.

### MSS Partition By

Some MSS prepared models include `partition_by = ["dl_current_indicator"]`
in the config. Check existing prepared models in the dc_tag folder.

### Column List

- List all business columns from the integration model output.
- Include `dl_source` as a business column.
- Do NOT include `seq` (the dedup column) -- it is filtered out in integration.
- Do NOT include `dl_checksum_value` in the explicit column list; reference
  it after the business columns since integration already computes it.

## File Location

- **IM:** `models/<dc_tag>/<entity_name>_f/prepared/<entity_name>.sql`
- **MSS:** `models/<dc_tag>/<entity_name>/prepared/<entity_name>.sql`

## Inputs Required

| Input | Description |
|-------|-------------|
| `entity_name` | Target entity name |
| `dataset_type` | `master` or `balance` |
| `as_of_col` | Business date column (balance only) |
| `pk_columns_list` | PK columns as Python list of strings |
| `business_column_list` | All business columns from integration output |
| `prepared_schema` | `cspn_fndn2_` or `cspn_cons2_` |
| `repo_type` | `im` or `mss` |
