# SQL-INCR: Incremental Models

Incremental materialization, merge strategy, lookback windows.

## SQL-INCR-001 — Don't use incremental as a default

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Start with `materialized='table'`. Switch to
`incremental` only when one of these is true:

- The source has more than ~10 million rows.
- The model has a reliable `updated_at` or `created_at` timestamp.
- Full refreshes exceed acceptable runtime (typically >10 minutes).

**Why.** Incremental models add operational complexity (full-refresh
correctness, lookback windows, schema evolution). Pay that complexity
only when you need it.

## SQL-INCR-002 — Use `merge` strategy on Databricks

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Always set `incremental_strategy='merge'` on Databricks.

**Why.** Handles inserts and updates atomically. Other strategies do not
on Delta tables.

**Examples.**
```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns',
    )
}}
```

## SQL-INCR-003 — `is_incremental()` filter in source CTE, not separate CTE

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** The `is_incremental()` block goes inside the CTE where
data is first read.

**Examples.**
```sql
-- ✓
with

events as (
    select *
    from {{ ref('stg_app__events') }}
    {% if is_incremental() %}
    where event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),

-- ✗ separate filtering CTE
with

events as (
    select * from {{ ref('stg_app__events') }}
),

filtered as (
    select *
    from events
    {% if is_incremental() %}
    where event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),
```

## SQL-INCR-004 — Compare against destination using `{{ this }}`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Inside `is_incremental()`, compare the source's high-water
mark against `(select max(...) from {{ this }})`.

**Why.** `{{ this }}` resolves to the destination table. Hardcoding the
table name breaks across environments.

## SQL-INCR-005 — Late-arriving data uses a documented lookback window

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a source can deliver data late (event streams,
third-party syncs), apply a lookback window with a comment explaining
the duration and the reason.

**Examples.**
```sql
{% if is_incremental() %}
-- 3-day lookback: Segment can deliver events up to 72 hours late
-- due to mobile SDK batching and retry behavior.
where event_timestamp > (
    select dateadd(day, -3, max(event_timestamp))
    from {{ this }}
)
{% endif %}
```

## SQL-INCR-006 — Incremental models must work on `--full-refresh`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every incremental model produces correct results on `dbt
run --full-refresh`. The `is_incremental()` block is skipped during full
refresh, so the model must be correct without the filter.

**Why.** Eventually you will need to rebuild. If `--full-refresh`
silently produces wrong data, that's a critical bug.

### Testing
