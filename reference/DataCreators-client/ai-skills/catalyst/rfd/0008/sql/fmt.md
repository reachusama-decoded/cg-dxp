# SQL-FMT: Formatting

Keyword case, indentation, joins, where, group by, case formatting.

## SQL-FMT-001 — Keywords lowercase

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `capitalisation.keywords`

**Decision.** All SQL keywords are lowercase.

**Why.** Uppercase SQL keywords are a relic of terminals without syntax
highlighting. Modern editors highlight automatically. Lowercase reads
naturally and matches dbt community convention.

**Examples.**
```sql
-- ✓
select column_name, count(*) as row_count
from catalog.schema.table
where status = 'active'
group by column_name

-- ✗
SELECT Column_Name, COUNT(*) AS row_count
FROM catalog.schema.table
WHERE status = 'active'
GROUP BY Column_Name
```

## SQL-FMT-002 — 4-space indentation, no tabs

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `layout.indent`

**Decision.** Indent with 4 spaces. No tabs. No 2-space indentation.

## SQL-FMT-003 — Trailing commas in select clauses

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `convention.select_trailing_comma`

**Decision.** Always trailing commas in select. No leading commas.

**Why.** Cleaner diffs — adding or removing the last column changes one
line, not two.

**Examples.**
```sql
-- ✓
select
    order_id,
    customer_id,
    order_date,
from orders

-- ✗ leading commas
select
    order_id
    , customer_id
    , order_date
from orders
```

## SQL-FMT-004 — Explicit join types; `on` on its own line

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `ambiguous.join`

**Decision.** Always write `inner join`, `left join`, `right join`, or
`full outer join` — never bare `join`. Put the `on` clause on its own
line, indented.

**Why.** Eliminates ambiguity for readers and tooling.

**Examples.**
```sql
-- ✓
from orders as o
inner join customers as c
    on o.customer_id = c.customer_id

-- ✓ multi-condition
from orders as o
inner join order_items as oi
    on o.order_id = oi.order_id
    and o.order_date = oi.order_date

-- ✗
from orders as o
inner join customers as c on o.customer_id = c.customer_id
```

## SQL-FMT-005 — No implicit comma joins

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `ambiguous.join`

**Decision.** Never use comma-separated tables in the `from` clause.

**Why.** Forgotten `where` conditions silently produce cross joins.

**Examples.**
```sql
-- ✗ implicit join
select o.order_id, c.customer_name,
from orders o, customers c
where o.customer_id = c.customer_id

-- ✓
from orders as o
inner join customers as c
    on o.customer_id = c.customer_id
```

## SQL-FMT-006 — Where conditions one per line; `and`/`or` at line start

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `layout.start_of_file`

**Decision.** Each `where` condition on its own line. `and`/`or` at the
start of the line, not the end.

**Examples.**
```sql
-- ✓
where status = 'active'
    and region = 'us-east'
    and amount > 100

-- ✗
where status = 'active' and
    region = 'us-east' and
    amount > 100
```

## SQL-FMT-007 — `group by` uses column names, not numbers

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `references.consistent`

**Decision.** Always reference columns by name in `group by`. Never use
`group by 1, 2`.

**Why.** Numeric references break when columns are reordered and are
opaque to reviewers.

## SQL-FMT-008 — `case` statements: one `when` per line

**Severity:** warning
**Since:** v0.1.0
**Linter:** SQLFluff `layout`

**Decision.** Format `case` with `when`/`then`/`else`/`end` each on their
own line, indented inside the `case`/`end` block.

**Examples.**
```sql
-- ✓
case
    when amount > 1000 then 'high'
    when amount > 100 then 'medium'
    else 'low'
end as order_tier
```

### Naming
