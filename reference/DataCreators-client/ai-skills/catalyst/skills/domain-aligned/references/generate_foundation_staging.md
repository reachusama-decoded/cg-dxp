# Generate Foundation Staging Models (Domain-Aligned, Multi-Source)

Create one staging SQL model per source table. Each staging model reads from
its respective source in the standard zone and passes all columns through.
Column renaming happens in the integration layer.

## Key Difference from Single-Source (entity-scaffold)

In domain-aligned pipelines, there are **multiple staging models** -- one per
source table. Each staging model outputs the same set of columns so they can
be UNIONed in the integration layer.

## IM Foundation Pattern (v4)

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        meta = { "dataset_load_type" : "incremental",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}

{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = "<source_schema_prefix>"|string + source_schema_suffix  %}

SELECT
  <column_1>,
  <column_2>,
  ...
  '<vendor_name>' AS dl_source
FROM {{ cspn_source_v2(source_schema, "<source_table>") }}
```

### IM Rules

- `source_schema` is built by concatenating the prefix (e.g., `cspn_std_rapid_`)
  with `var("source_schema_suffix")`.
- Use `cspn_source_v2(source_schema, "table_name")` macro.
- List every column from the source table explicitly -- never use `SELECT *`.
- Column names remain in their original case (camelCase) at the staging layer.
- Config meta includes `dataset_load_type` and `dataset_load_catchup_strategy`.
- Add `'<vendor_name>' AS dl_source` to track which source provided the row.

## MSS Foundation Pattern

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized = 'view',
        meta = { "dataset_load_type" : "incremental",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}

{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = "<source_schema_prefix>"|string + source_schema_suffix  %}

SELECT
  <column_1>,
  <column_2>,
  ...
  '<vendor_name>' AS dl_source
FROM {{ cspn_source(source_schema, "<source_table>") }}
```

### MSS Rules

- Use `cspn_source(source_schema, "table_name")` macro (not `_v2`).
- Some MSS models use `{{ source('source_name', 'table_name') }}` instead.
  Check existing models in the same dc_tag folder for the convention in use.
- Materialized as `view` explicitly stated in config.

## Column Alignment Across Staging Models

Since all staging models will be UNIONed, their output columns must be aligned:

1. **Identify the canonical column set** from the model specification (Step 2 output).
2. **Each staging model** must output exactly these columns, in the same order.
3. If a source table does not have a particular column, use:
   ```sql
   CAST(NULL AS <target_type>) AS <column_name>
   ```
4. If a source table names a column differently, rename it in the SELECT:
   ```sql
   <source_column_name> AS <canonical_column_name>
   ```
5. Use CAST to normalize types across sources.

## File Location

- **IM:** `models/<dc_tag>/<entity_name>_f/staging/stage_<source_table>.sql`
- **MSS:** `models/<dc_tag>/<entity_name>/staging/stage_<source_table>.sql`

Generate one file per source table. File name uses the source table name
(e.g., `stage_rapid_security_bloomberg_f1_v1_t1.sql`).

## Inputs Required

| Input | Description |
|-------|-------------|
| `source_tables` | List of source table names with their schemas |
| `source_schema_prefix` | Schema prefix per source (e.g., `cspn_std_rapid_`) |
| `canonical_columns` | The unified column set from the model spec |
| `vendor_names` | Vendor identifier per source table |
| `repo_type` | `im` or `mss` |

## Example: Two-Source IM Staging

### stage_rapid_security_bloomberg_f1_v1_t1.sql

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        meta = { "dataset_load_type" : "incremental",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}

{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = "cspn_std_rapid_"|string + source_schema_suffix  %}

SELECT
  securityuid,
  securityname,
  issuercountrycode,
  currencycode,
  maturitydate,
  couponrate,
  'bloomberg' AS dl_source
FROM {{ cspn_source_v2(source_schema, "rapid_security_bloomberg_f1_v1_t1") }}
```

### stage_rapid_security_refinitiv_f1_v1_t1.sql

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        meta = { "dataset_load_type" : "incremental",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}

{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = "cspn_std_rapid_"|string + source_schema_suffix  %}

SELECT
  security_id AS securityuid,
  security_desc AS securityname,
  country_of_issue AS issuercountrycode,
  trading_currency AS currencycode,
  maturity_dt AS maturitydate,
  cpn_rate AS couponrate,
  'refinitiv' AS dl_source
FROM {{ cspn_source_v2(source_schema, "rapid_security_refinitiv_f1_v1_t1") }}
```

Note how the Refinitiv staging model renames columns to match Bloomberg's
naming, ensuring both produce identical column sets for the UNION.
