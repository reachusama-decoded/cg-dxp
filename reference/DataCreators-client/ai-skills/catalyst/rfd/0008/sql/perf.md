# SQL-PERF: Performance

Partition pruning, Z-ORDER, expensive operations, window functions.

## SQL-PERF-001 — Include partition column in `where` for partition pruning

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When querying a partitioned table on Databricks, include
the partition column in the `where` clause. Without it, Databricks scans
every partition.

**Examples.**
```sql
-- ✗ full table scan
select *
from events
where event_type = 'purchase'

-- ✓ partition pruning on event_date
select *
from events
where event_date >= '2026-01-01'
    and event_type = 'purchase'
```

## SQL-PERF-002 — Z-ORDER on frequently filtered/joined columns; max 4

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Configure `zorder` in the model config (not in post-hooks)
on columns frequently used in `where` and `join`. Maximum 4 columns —
effectiveness drops with each addition. Highest-cardinality filtered
column first.

**Examples.**
```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        file_format='delta',
        zorder=['customer_id', 'event_date'],
    )
}}
```

## SQL-PERF-003 — Avoid `distinct` on large tables

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** `distinct` on large tables forces a full shuffle. Fix the
upstream join or use `group by` instead.

## SQL-PERF-004 — `order by` only in final reporting models

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't `order by` in intermediate models. The sort is
discarded by downstream operations and pays for itself only in
user-facing reports.

## SQL-PERF-005 — `union all` over `union`

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `convention`

**Decision.** Use `union all`. Use `union` (with implicit deduplication)
only when you genuinely need it.

**Why.** `union` triggers an implicit `distinct` across both sides.
`union all` is strictly cheaper unless deduplication is required.

## SQL-PERF-006 — Avoid correlated subqueries; use joins or window functions

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Correlated subqueries execute once per outer row.
Restructure as a join or a window function.

### Security
