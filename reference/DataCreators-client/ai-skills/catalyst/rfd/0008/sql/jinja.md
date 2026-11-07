# SQL-JINJA: Jinja and Macros

Macro discipline, template-vs-code separation, env_var policy.

## SQL-JINJA-001 — Macros for SQL repeated in 3+ models

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Extract a macro when the same SQL pattern appears in 3 or
more models.

**Why.** DRY — but only when it actually pays off. A macro called from
one place is harder to read than the inline SQL.

## SQL-JINJA-002 — No macros for one-off or complex business logic

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't build macros for one-off logic. Don't put complex
business rules in Jinja — they belong in SQL.

## SQL-JINJA-003 — Macros named in `snake_case`; describe what they generate

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Macro names are `snake_case` and describe the SQL they
produce.

**Examples.**
```
✓ macros/generate_surrogate_key.sql
✓ macros/cents_to_dollars.sql
✓ macros/union_staging_tables.sql

✗ macros/helper.sql
✗ macros/util.sql
✗ macros/my_macro.sql
```

## SQL-JINJA-004 — Keep business logic in SQL, not Jinja

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Jinja generates SQL. SQL encodes business rules. If a
Jinja block exceeds ~10 lines of control flow, refactor into SQL.

**Examples.**
```sql
-- ✗ business logic in Jinja
{% set tiers = [
    ('enterprise', 10000),
    ('mid_market', 1000),
    ('smb', 0),
] %}

select
    order_id,
    {% for tier_name, threshold in tiers %}
    {% if not loop.last %}
    case when amount >= {{ threshold }} then '{{ tier_name }}'
    {% else %}
    else '{{ tier_name }}' end as deal_tier,
    {% endif %}
    {% endfor %}
from orders

-- ✓ business logic in SQL
select
    order_id,
    case
        when amount >= 10000 then 'enterprise'
        when amount >= 1000 then 'mid_market'
        else 'smb'
    end as deal_tier,
from orders
```

## SQL-JINJA-005 — Jinja loops acceptable for repetitive column generation

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Jinja loops are fine for generating repetitive column
lists from a known schema — not for encoding business rules.

**Examples.**
```sql
-- ✓ DRY column generation
{% set payment_methods = ['credit_card', 'bank_transfer', 'paypal'] %}

select
    order_id,
    {% for method in payment_methods %}
    sum(case when payment_method = '{{ method }}' then amount else 0 end)
        as {{ method }}_amount,
    {% endfor %}
from payments
group by order_id
```

## SQL-JINJA-006 — `env_var()` in `profiles.yml` only, never in model SQL

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Read environment variables in `profiles.yml` and
`dbt_project.yml` only. Never use `env_var()` inside model SQL files.

**Why.** Model SQL should be deterministic for the given target. Reading
environment in models breaks reproducibility and lineage.

### Idioms (Anti-pattern Inverses)
