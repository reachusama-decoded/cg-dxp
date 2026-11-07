# SQL-TEST: Testing

Generic tests, singular tests, dbt unit tests, severity policy.

## SQL-TEST-001 — `unique` + `not_null` on every primary key

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Every model's primary-key column has `unique` and
`not_null` data tests in the model's schema YAML.

## SQL-TEST-002 — `not_null` + `relationships` on every foreign key

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Every foreign-key column has `not_null` (unless the join
is optional/left) and `relationships` pointing to the parent model.

**Examples.**
```yaml
columns:
  - name: customer_id
    data_tests:
      - not_null
      - relationships:
          to: ref('dim_customers')
          field: customer_id
```

## SQL-TEST-003 — `accepted_values` on enum-like columns

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Columns with a known finite set of values declare them via
`accepted_values`.

**Examples.**
```yaml
columns:
  - name: order_status
    data_tests:
      - accepted_values:
          values: ['pending', 'shipped', 'delivered', 'cancelled', 'returned']
```

## SQL-TEST-004 — Singular tests return zero rows to pass

**Severity:** error
**Since:** v0.1.0
**Linter:** dbt convention

**Decision.** Singular tests are SQL files in `tests/` that return zero
rows when the assertion holds.

**Examples.**
```sql
-- tests/assert_no_orphaned_order_items.sql
select oi.order_item_id
from {{ ref('fct_order_items') }} as oi
left join {{ ref('int_orders__enriched') }} as o
    on oi.order_id = o.order_id
where o.order_id is null
```

## SQL-TEST-005 — Unit tests required for business logic

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Models containing business logic (case statements,
conditional aggregations, complex joins) have unit tests with explicit
inputs and expected outputs (dbt 1.8+).

**Examples.**
```yaml
unit_tests:
  - name: test_deal_tier_classification
    model: int_orders__enriched
    given:
      - input: ref('stg_salesforce__orders')
        rows:
          - { order_id: 1, amount: 15000, customer_id: 'c1' }
          - { order_id: 2, amount: 5000, customer_id: 'c2' }
          - { order_id: 3, amount: 500, customer_id: 'c3' }
    expect:
      rows:
        - { order_id: 1, deal_tier: 'enterprise' }
        - { order_id: 2, deal_tier: 'mid_market' }
        - { order_id: 3, deal_tier: 'smb' }
```

## SQL-TEST-006 — `severity: warn` for non-blocking; `error` for blocking

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `severity: warn` for data-quality issues that are
informational. Use `error` (the default) for issues that must block the
pipeline.

**Examples.**
```yaml
columns:
  - name: email
    data_tests:
      - not_null:
          severity: warn
      - unique:
          severity: error
```

### Jinja and Macros
