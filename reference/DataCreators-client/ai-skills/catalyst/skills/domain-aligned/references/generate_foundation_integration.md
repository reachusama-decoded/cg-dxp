# Generate Foundation Integration Model (Domain-Aligned, Multi-Source UNION)

Create the integration SQL model that UNIONs all staging models, renames
columns from camelCase to snake_case, deduplicates rows, and computes a
checksum.

## Key Difference from Single-Source (entity-scaffold)

In domain-aligned pipelines, the integration model **UNIONs multiple staging
models** before applying dedup and checksum. The `_union` suffix in the model
name distinguishes this from single-source integration models.

## Template

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized='view'
    )
}}

{% set dleffectivedate = var('app_cycle_date') |string %}

WITH union_cte AS (
    SELECT * FROM {{ref('stage_<source_1>')}}
    UNION ALL
    SELECT * FROM {{ref('stage_<source_2>')}}
    UNION ALL
    SELECT * FROM {{ref('stage_<source_3>')}}
),

renamed_cte AS (
SELECT
  -- Column renames: camelCase --> snake_case
  <source_col_1> AS <snake_case_col_1>,
  <source_col_2> AS <snake_case_col_2>,
  ...
  dl_source,

  -- Dedup via ROW_NUMBER (partition by PK columns, order by timestamp DESC)
  ROW_NUMBER() OVER (
    PARTITION BY <pk_source_columns>
    ORDER BY <order_column> DESC
  ) seq
  FROM union_cte
)

SELECT
  <snake_case_column_list>,
  dl_source,
  sha1(concat_ws('|',
      <checksum_column_list>
  )) AS dl_checksum_value
FROM renamed_cte
WHERE seq = 1
```

## Column Rename Rules

- Convert camelCase to snake_case (e.g., `securityUid` --> `security_uid`).
- Add meaningful suffixes where appropriate:
  - `*date` columns: keep `_date` or use `_timestamp` if timestamp type.
  - `*code` columns: keep `_code`.
  - `*indicator` columns: normalize to boolean Y/N pattern.
  - `*amount` columns: keep `_amount`.
  - `*number` columns: keep `_number` or `_uid`.
- Look at existing integration models in the same dc_tag folder for naming
  precedents.

## Boolean Normalization

For any column that represents a boolean/indicator value:

```sql
CASE WHEN <original_col> IN ("T", "True", "1") THEN 'Y'
     WHEN <original_col> IN ("F", "FALSE", "0") THEN 'N'
     ELSE NULL END AS <snake_case_col>
```

## Dedup Pattern (Cross-Source)

When deduplicating across multiple sources:

- Use `ROW_NUMBER() OVER (PARTITION BY <pk_cols> ORDER BY <timestamp_col> DESC)`.
- The partition columns should be the PK columns (canonical, post-rename).
- The order column is typically a processing timestamp or running date.
- If the same entity appears in multiple sources, the dedup ensures only one
  row per natural key survives. Consider adding `dl_source` to the ORDER BY
  to establish a consistent source priority:
  ```sql
  ROW_NUMBER() OVER (
    PARTITION BY security_uid
    ORDER BY running_timestamp DESC,
             CASE dl_source
               WHEN 'bloomberg' THEN 1
               WHEN 'refinitiv' THEN 2
               ELSE 99
             END
  ) seq
  ```
- If an `actioncode` column exists, include it in the ORDER BY:
  `ORDER BY <timestamp_col> DESC, actioncode DESC`.
- Filter `WHERE seq = 1` in the outer SELECT.

## Checksum Computation

- Use `sha1(concat_ws('|', ...))` with all business columns.
- For string columns, wrap with `TRIM(COALESCE(<col>, ''))`.
- For numeric/date columns, include as-is or cast appropriately.
- Include `dl_source` in the checksum if source provenance is part of the
  business data.
- Name the output column `dl_checksum_value`.

## MSS Variant

MSS integration models may use `insert_overwrite` instead of `view`:

```sql
{{
    config(
        schema = "cspn_work2_" |string + target.name,
        materialized = 'incremental',
        incremental_strategy = 'insert_overwrite',
        file_format = 'parquet',
        location_root = "s3://datalake-curated-" |string + target.name + "-us-east-1/cspn_work2" |string
    )
}}
```

Check existing integration models in the dc_tag folder to confirm which
materialization strategy is used.

## File Location

- **IM:** `models/<dc_tag>/<entity_name>_f/integration/int_<entity_name>_union.sql`
- **MSS:** `models/<dc_tag>/<entity_name>/integration/int_<entity_name>_union.sql`

Note the `_union` suffix to distinguish multi-source from single-source
integration models.

## Inputs Required

| Input | Description |
|-------|-------------|
| `entity_name` | Target entity name |
| `staging_model_names` | List of staging model names to UNION |
| `pk_columns` | PK columns (post-rename, snake_case) for dedup PARTITION BY |
| `order_column` | Timestamp column for dedup ordering |
| `column_renames` | Mapping of source columns to snake_case names |
| `boolean_columns` | List of columns to normalize as Y/N |
| `source_priority` | (optional) Priority order for source dedup tiebreaker |
| `repo_type` | `im` or `mss` |

## Example: Two-Source IM Integration

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized='view'
    )
}}

{% set dleffectivedate = var('app_cycle_date') |string %}

WITH union_cte AS (
    SELECT * FROM {{ref('stage_rapid_security_bloomberg_f1_v1_t1')}}
    UNION ALL
    SELECT * FROM {{ref('stage_rapid_security_refinitiv_f1_v1_t1')}}
),

renamed_cte AS (
SELECT
  securityuid AS security_uid,
  securityname AS security_name,
  issuercountrycode AS issuer_country_code,
  currencycode AS currency_code,
  maturitydate AS maturity_date,
  couponrate AS coupon_rate,
  dl_source,
  ROW_NUMBER() OVER (
    PARTITION BY securityuid
    ORDER BY maturitydate DESC,
             CASE dl_source
               WHEN 'bloomberg' THEN 1
               WHEN 'refinitiv' THEN 2
               ELSE 99
             END
  ) seq
  FROM union_cte
)

SELECT
  security_uid,
  security_name,
  issuer_country_code,
  currency_code,
  maturity_date,
  coupon_rate,
  dl_source,
  sha1(concat_ws('|',
      security_uid,
      TRIM(COALESCE(security_name, '')),
      TRIM(COALESCE(issuer_country_code, '')),
      TRIM(COALESCE(currency_code, '')),
      cast(maturity_date AS date),
      coupon_rate,
      TRIM(COALESCE(dl_source, ''))
  )) AS dl_checksum_value
FROM renamed_cte
WHERE seq = 1
```
