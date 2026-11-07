# dbt Canonical Model Generation — Domain-Aligned

You are generating dbt models for a **domain-aligned canonical data product**. The input is a model specification YAML that defines a canonical table built from multiple Unity Catalog source tables.

## Architecture

```
Source Tables (UC)
    ↓
Staging (one per source) — rename columns, cast types, add dl_source
    ↓
Intermediate — UNION ALL of staging models
    ↓
Canonical — surrogate key, bi-temporal columns, incremental merge
```

## Critical Rule: UNION, Not JOIN

Domain-aligned canonical models **UNION datasets from multiple vendors/sources into a single canonical table**. Each source provides the same entity (e.g., securities) but from different vendors (e.g., Bloomberg, Refinitiv, MSCI).

- **UNION ALL** — always use UNION ALL (not UNION) to preserve all rows
- **Column standardization** happens in the staging layer, not in the UNION
- **JOIN** is only used in rare denormalized models — never for the default canonical pattern

## Staging Model Pattern

Generate one staging model per source table: `stg_<vendor>_<entity>.sql`

```sql
{{ config(materialized='view') }}

{# Staging model for <vendor> <entity> data #}
{# Source: <catalog>.<schema>.<table> #}

SELECT
    -- Natural key columns (must match across all staging models)
    CAST(<source_key_col> AS STRING) AS <canonical_key_col>,

    -- Business columns (renamed to canonical names)
    CAST(<source_col_1> AS <target_type>) AS <canonical_col_1>,
    CAST(<source_col_2> AS <target_type>) AS <canonical_col_2>,

    -- Source tracking
    '<vendor_name>' AS dl_source,

    -- System timestamp
    CURRENT_TIMESTAMP() AS dl_system_from_date

FROM {{ source('<source_name>', '<table_name>') }}
```

**Rules:**
- Every staging model must output **identical column names and types**
- Use CAST to normalize types across vendors
- Add `dl_source` literal string for provenance
- Use `view` materialization (no need to persist staging)
- If a source doesn't have a column, use `CAST(NULL AS <type>) AS <col_name>`

## Intermediate Model Pattern

Generate one intermediate model: `int_<model>_union.sql`

```sql
{{ config(materialized='view') }}

{# Union of all source staging models for <model> #}

SELECT * FROM {{ ref('stg_<vendor1>_<entity>') }}
UNION ALL
SELECT * FROM {{ ref('stg_<vendor2>_<entity>') }}
UNION ALL
SELECT * FROM {{ ref('stg_<vendor3>_<entity>') }}
```

**Rules:**
- UNION ALL of all staging models
- Materialized as `view` — no persistence needed
- Column order must match (guaranteed by staging layer)

## Canonical Model Pattern

Generate the final canonical model: `<model>.sql`

```sql
{{
  config(
    materialized='incremental',
    unique_key='dl_row_uid',
    incremental_strategy='merge',
    schema=env_var('DATABRICKS_DEFAULT_SCHEMA'),
    file_format='delta',
    meta={
      'surrogate_key_cols': ['<natural_key_col1>', '<natural_key_col2>'],
      'load_type': '<master|balance>'
    }
  )
}}

WITH source_data AS (
    SELECT * FROM {{ ref('int_<model>_union') }}
),

enriched AS (
    SELECT
        -- Surrogate key
        {{ generate_surrogate_key_v3(['<natural_key_col1>', '<natural_key_col2>']) }} AS dl_row_uid,

        -- All business columns from intermediate
        <canonical_col_1>,
        <canonical_col_2>,
        ...,

        -- Source tracking (from staging)
        dl_source,

        -- Bi-temporal audit columns
        CURRENT_TIMESTAMP() AS dl_business_from_date,
        CAST('9999-12-31' AS TIMESTAMP) AS dl_business_to_date,
        dl_system_from_date,
        CAST(NULL AS TIMESTAMP) AS dl_system_to_date,
        TRUE AS is_current,

        -- Change detection
        MD5(CONCAT_WS('||',
            COALESCE(CAST(<canonical_col_1> AS STRING), ''),
            COALESCE(CAST(<canonical_col_2> AS STRING), ''),
            ...
        )) AS checksum

    FROM source_data
)

SELECT * FROM enriched

{% if is_incremental() %}
WHERE dl_system_from_date > (SELECT MAX(dl_system_from_date) FROM {{ this }})
{% endif %}
```

**Rules:**
- `dl_row_uid` is the surrogate key via `generate_surrogate_key_v3()`
- Pass the natural key columns list to the macro
- `schema` from `env_var('DATABRICKS_DEFAULT_SCHEMA')` — never hardcode
- Include ALL bi-temporal columns
- `checksum` uses MD5 of concatenated business columns for change detection
- Incremental filter on `dl_system_from_date`
- `load_type`: Use `master` for dimension-like tables, `balance` for fact-like tables

## Column Naming Convention

| Column | Type | Purpose |
|--------|------|---------|
| `dl_row_uid` | STRING | Surrogate key (MD5 of natural keys) |
| `dl_source` | STRING | Source system/vendor identifier |
| `dl_business_from_date` | TIMESTAMP | Business validity start |
| `dl_business_to_date` | TIMESTAMP | Business validity end (9999-12-31 if current) |
| `dl_system_from_date` | TIMESTAMP | Record ingestion time |
| `dl_system_to_date` | TIMESTAMP | Record superseded time (NULL if current) |
| `is_current` | BOOLEAN | TRUE for latest version of each key |
| `checksum` | STRING | MD5 hash for change detection |

## Schema YAML Pattern

See `prompts/dbt_schema_yml.md` for the schema.yml generation pattern.

## Validation Checklist

Before marking generation as complete:
- [ ] All staging models have identical column names and types
- [ ] Intermediate model UNIONs ALL staging models
- [ ] Canonical model has surrogate key, all bi-temporal columns
- [ ] No hardcoded catalog/schema names — only `env_var()` and `{{ source() }}`/`{{ ref() }}`
- [ ] Schema YAML has `not_null` + `unique` on `dl_row_uid`
- [ ] `dbt_project.yml` and `profiles.yml` are valid
