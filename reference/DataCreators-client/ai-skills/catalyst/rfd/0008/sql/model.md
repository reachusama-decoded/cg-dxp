# SQL-MODEL: Model Organization

Model organization, ref/source, schema YAML, staging discipline.

## SQL-MODEL-001 — One model per file

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Never put multiple models in a single `.sql` file.

## SQL-MODEL-002 — Always `ref()` and `source()`; never hardcode table names

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** All references to dbt-managed tables use `{{ ref('...') }}`.
All references to external/raw tables use `{{ source('...', '...') }}`.
Never hardcoded `catalog.schema.table` strings.

**Why.** This is the single most important dbt rule. Hardcoded table
names break the DAG, bypass environment switching, and prevent dbt from
tracking lineage.

**Examples.**
```sql
-- ✓
select * from {{ ref('stg_salesforce__accounts') }}
select * from {{ source('salesforce', 'accounts') }}

-- ✗
select * from analytics.stg_salesforce__accounts
```

## SQL-MODEL-003 — Never use `{{ target.schema }}` for table references

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't build table references with `{{ target.schema }}`.
Use `ref()` or `source()`.

**Why.** `target.schema` re-implements `ref()` badly — without lineage,
without dependency tracking, without environment isolation.

## SQL-MODEL-004 — Co-locate `schema.yml` with models

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every model directory contains a `schema.yml` (or
`_schema.yml` / `_{directory_name}.yml`) that defines all models in that
directory.

## SQL-MODEL-005 — Directory structure follows the DAG

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Models live under `models/` in directories that mirror the
DAG layers:

```
models/
    staging/
        salesforce/
            _salesforce__sources.yml
            _salesforce__models.yml
            stg_salesforce__accounts.sql
            stg_salesforce__opportunities.sql
        stripe/
            _stripe__sources.yml
            _stripe__models.yml
            stg_stripe__payments.sql
    intermediate/
        _int__models.yml
        int_orders__enriched.sql
        int_customer__lifetime_value.sql
    marts/
        _marts__models.yml
        fct_order_items.sql
        fct_daily_revenue.sql
        dim_customers.sql
        dim_products.sql
```

## SQL-MODEL-006 — Config block at top of file, before first CTE

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Model `config()` blocks come before the first `with`. Use
`config()`, not `dbt_project.yml`, for model-specific settings.
`dbt_project.yml` is for directory-level defaults only.

**Examples.**
```sql
{{
    config(
        materialized='table',
        tags=['daily', 'finance'],
    )
}}

with

source as (
    ...
)
```

## SQL-MODEL-007 — Every model has a schema YAML entry with description and primary-key tests

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Every model has an entry in a co-located `schema.yml` with
at minimum: a description, and column-level tests for the primary key.

**Examples.**
```yaml
models:
  - name: fct_order_items
    description: >
      One row per order line item. Grain is order_item_id.
    columns:
      - name: order_item_id
        description: Primary key.
        data_tests:
          - unique
          - not_null
      - name: order_id
        description: Foreign key to fct_orders.
        data_tests:
          - not_null
          - relationships:
              to: ref('int_orders__enriched')
              field: order_id
```

## SQL-MODEL-008 — Staging models do rename and recast only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Staging models contain no joins, no aggregations, no
business logic. Only column rename and type cast.

**Why.** Staging is the contract layer between raw and curated. Mixing
business logic in here makes the contract opaque.

**Examples.**
```sql
-- models/staging/salesforce/stg_salesforce__accounts.sql

with

source as (
    select * from {{ source('salesforce', 'accounts') }}
),

renamed as (
    select
        id as account_id,
        name as account_name,
        cast(created_date as date) as created_date,
        cast(annual_revenue as decimal(18, 2)) as annual_revenue,
        is_deleted as is_deleted,
        cast(_fivetran_synced as timestamp) as synced_at,
    from source
    where not is_deleted
)

select * from renamed
```

### Incremental Models
