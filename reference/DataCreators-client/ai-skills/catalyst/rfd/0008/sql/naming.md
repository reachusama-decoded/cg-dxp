# SQL-NAMING: Naming

Model prefixes, source naming, column conventions, test naming.

## SQL-NAMING-001 — Model prefixes required

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Every dbt model has one of these prefixes:

| Prefix | Layer | Purpose |
|--------|-------|---------|
| `stg_` | Staging | 1:1 with source — rename and recast only |
| `int_` | Intermediate | Business logic, joins, aggregations between staging models |
| `fct_` | Fact | Event or transactional grain, immutable once loaded |
| `dim_` | Dimension | Slowly changing descriptive entities |
| `rpt_` | Report | Aggregated/denormalized for a specific consumer or dashboard |
| `snap_` | Snapshot | dbt snapshot for SCD Type 2 tracking |
| `base_` | Base | Intermediate step within staging when a single source needs multi-step cleaning |

**Why.** Prefix communicates the model's role in the DAG at a glance.

**Exception.** None.

## SQL-NAMING-002 — Source naming matches external system; staging follows `stg_{source}__{table}`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Source names in `schema.yml` match the external system
name. Table names match the physical table exactly. Staging models
follow the pattern `stg_{source}__{table}` with a double underscore
separating source system from table name.

**Examples.**
```yaml
sources:
  - name: salesforce
    schema: raw_salesforce
    tables:
      - name: accounts
      - name: opportunities
```

```
stg_salesforce__accounts.sql
stg_salesforce__opportunities.sql
stg_stripe__payments.sql
```

## SQL-NAMING-003 — Column naming conventions

**Severity:** error
**Since:** v0.1.0
**Linter:** SQLFluff `capitalisation.identifiers`

**Decision.** All columns are `snake_case`. Use the suffixes in this
table for clarity:

| Rule | Convention | Example |
|------|-----------|---------|
| All columns | `snake_case` | `order_date`, `customer_id` |
| Boolean columns | `is_` or `has_` prefix | `is_active`, `has_subscription` |
| Date columns | `_date` suffix | `order_date`, `created_date` |
| Timestamp columns | `_at` suffix | `created_at`, `updated_at` |
| ID columns | `_id` suffix | `customer_id`, `order_id` |
| Count metrics | `_count` suffix | `order_count`, `item_count` |
| Dollar amounts | `_amount` suffix | `order_amount`, `refund_amount` |
| Ratios/percentages | `_pct` or `_rate` suffix | `conversion_rate`, `null_pct` |

**Why.** Predictable column shapes mean readers don't have to guess
whether `created` is a date or a timestamp.

**Exception.** Reserved SQL keywords as bare column names (`date`,
`type`, `status`) are discouraged — prefer `order_date`, `account_type`,
`order_status`.

## SQL-NAMING-004 — Singular test files describe the assertion

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Singular tests in `tests/` are named for what they assert.

**Examples.**
```
tests/assert_order_amounts_are_positive.sql
tests/assert_no_orphaned_order_items.sql
tests/assert_revenue_reconciles_to_source.sql
```

### CTE Patterns
