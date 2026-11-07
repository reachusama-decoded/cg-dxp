# SQL-IDIOM: Idioms

Anti-pattern inverses: select *, subqueries, OR joins, distinct fixes.

## SQL-IDIOM-001 — `select *` only in import CTEs

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** `select *` is allowed only in import CTEs (the first CTEs
that reference `ref()` or `source()`). In all other CTEs, list columns
explicitly.

**Why.** `select *` in logic CTEs makes it impossible to know the schema
without tracing every upstream CTE. It also breaks when upstream columns
are added or renamed.

## SQL-IDIOM-002 — CTEs over subqueries in `from`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Never put a subquery in a `from` clause. Use CTEs.

**Examples.**
```sql
-- ✗
select customer_id, total_orders,
from (
    select customer_id, count(*) as total_orders,
    from (
        select * from orders where status != 'cancelled'
    ) as filtered
    group by customer_id
) as counted
where total_orders > 5

-- ✓
with
active_orders as (
    select * from orders where status != 'cancelled'
),
order_counts as (
    select customer_id, count(*) as total_orders,
    from active_orders
    group by customer_id
),
final as (
    select customer_id, total_orders,
    from order_counts
    where total_orders > 5
)
select * from final
```

## SQL-IDIOM-003 — No hardcoded dates or magic numbers

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't hardcode dates, environment names, or magic numbers
in model SQL. Use `var()` or compute dynamically.

**Examples.**
```sql
-- ✗
where order_date >= '2024-01-01'

-- ✓ dbt var
where order_date >= '{{ var("reporting_start_date") }}'

-- ✓ dynamic
where order_date >= dateadd(month, -12, current_date())
```

## SQL-IDIOM-004 — No `or` in join conditions

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Never use `or` in `on` clauses. Restructure as separate
joins or `union all`.

**Why.** `or` in joins produces unexpected cartesian products and is
almost always a logic error.

**Examples.**
```sql
-- ✗
inner join customers as c
    on o.billing_customer_id = c.customer_id
    or o.shipping_customer_id = c.customer_id

-- ✓ separate joins
with
billing_customer as (
    select o.order_id, c.customer_name as billing_customer_name,
    from orders as o
    inner join customers as c on o.billing_customer_id = c.customer_id
),
shipping_customer as (
    select o.order_id, c.customer_name as shipping_customer_name,
    from orders as o
    inner join customers as c on o.shipping_customer_id = c.customer_id
),
final as (
    select bc.order_id, bc.billing_customer_name, sc.shipping_customer_name,
    from billing_customer as bc
    left join shipping_customer as sc on bc.order_id = sc.order_id
)
select * from final
```

## SQL-IDIOM-005 — Never `distinct` to fix duplicates

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't use `distinct` to fix unexpected duplicates. Find
the root cause — almost always a fanout join — and fix it.

**Why.** `distinct` masks the real bug and makes the query expensive.

**Examples.**
```sql
-- ✗ DISTINCT to hide a fanout join
select distinct
    o.order_id, o.order_date, o.amount,
from orders as o
inner join order_tags as t on o.order_id = t.order_id

-- ✓ aggregate the many-side first
with
order_tag_count as (
    select order_id, count(*) as tag_count,
    from order_tags
    group by order_id
),
final as (
    select o.order_id, o.order_date, o.amount, otc.tag_count,
    from orders as o
    left join order_tag_count as otc on o.order_id = otc.order_id
)
select * from final
```

## SQL-IDIOM-006 — Window functions over self-joins for row-level comparisons

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When comparing rows within the same dataset (previous
order, running total, rank), use window functions, not self-joins.

**Examples.**
```sql
-- ✗
select o1.order_id, o1.order_date, o2.order_date as previous_order_date,
from orders as o1
left join orders as o2
    on o1.customer_id = o2.customer_id
    and o2.order_date < o1.order_date
    and o2.row_num = o1.row_num - 1

-- ✓
select
    order_id,
    order_date,
    lag(order_date) over (
        partition by customer_id
        order by order_date
    ) as previous_order_date,
from orders
```

### Performance
