# SQL-CTE: CTE Patterns

CTE patterns: import CTEs, single-step rule, final CTE convention.

## SQL-CTE-001 — CTEs over subqueries for non-trivial queries

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every non-trivial query uses CTEs. Subqueries are banned
except in `where ... in (select ...)` clauses where the subquery is a
simple single-column lookup.

**Why.** CTEs make the structure of a query reviewable. Nested
subqueries do not.

## SQL-CTE-002 — One logical step per CTE

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Each CTE does one thing — filter, join, aggregate, or
transform. If a CTE does more than one, split it.

## SQL-CTE-003 — Descriptive CTE names

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** CTE names describe the data in the CTE, not the operation.
`filtered_orders` is acceptable. `step_2` is not.

## SQL-CTE-004 — Import CTEs first

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** The first CTEs in any model are "import CTEs" that
reference sources or other models. This puts every dependency in one
place.

**Examples.**
```sql
with

orders as (
    select * from {{ ref('stg_salesforce__orders') }}
),

customers as (
    select * from {{ ref('stg_salesforce__customers') }}
),

payments as (
    select * from {{ ref('stg_stripe__payments') }}
),

-- logic CTEs follow
order_totals as (
    select
        order_id,
        sum(amount) as total_amount,
    from orders
    group by order_id
),
...
```

## SQL-CTE-005 — Final CTE named `final`; query ends with `select * from final`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** The last CTE is named `final`. The query ends with `select
* from final`. This makes every model's output immediately clear.

## SQL-CTE-006 — No nested CTEs

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** CTEs cannot contain `with` clauses inside them.

**Why.** Nested `with` defeats the purpose of using CTEs in the first
place — readability.

## SQL-CTE-007 — Blank line between CTEs

**Severity:** warning
**Since:** v0.1.0
**Linter:** SQLFluff `layout.spacing`

**Decision.** Separate each CTE with one blank line.

### Model Organization
