# Instructor legacy stretch answers — dbt

Preserved from `challenges/v2/dbt/phase-two-proficient/stretch/README.md` before separation. These legacy exercises retain their separate v1 runtime and access requirements; they are not evidence of v2 live execution. No real notification or external publishing is authorized.
## Answer 1: Solution

Three CTEs read the staging models; a `joined` CTE left-joins prices on (instrument, date) and FX on (local ccy → GBP, date), then computes the base-currency MV. The `coalesce(fx_rate, 1.0)` guards the left join: when no rate exists for that currency and date, `fx_rate` is `null` and the multiplication would erase the value, so the default of `1.0` leaves the holding at its local value.

```sql
with holdings as (
    select * from {{ ref('stg_holdings') }}
),
prices as (
    select * from {{ ref('stg_prices') }}
),
fx as (
    select * from {{ ref('stg_fx_rates') }}
),
joined as (
    select
        h.fund_id,
        h.position_date,
        h.instrument_id,
        h.quantity,
        h.mv_local_ccy,
        h.local_ccy,
        p.close_price,
        f.fx_rate                                   as fx_rate_to_base,
        h.mv_local_ccy * coalesce(f.fx_rate, 1.0)   as mv_base_ccy
    from holdings h
    left join prices p
        on p.instrument_id = h.instrument_id
        and p.price_date = h.position_date
    left join fx f
        on f.from_ccy = h.local_ccy
        and f.to_ccy = 'GBP'
        and f.rate_date = h.position_date
)
select * from joined
```

Reference: `solution/models/intermediate/int_holdings_enriched.sql`.


## Answer 2: Solution

Both are single-select re-shapes. `int_fund_attributes` filters to active funds; `int_positions_dated` sums cash and accrued into one column.

```sql
-- int_fund_attributes.sql
with funds as (
    select * from {{ ref('stg_funds') }}
)
select
    fund_id, fund_name, inception_date, base_ccy, strategy_code
from funds
where is_active = true
```

```sql
-- int_positions_dated.sql
with positions as (
    select * from {{ ref('stg_positions') }}
)
select
    fund_id,
    position_date,
    local_ccy,
    cash_balance + accrued_interest as cash_plus_accrued
from positions
```

Reference: `solution/models/intermediate/int_fund_attributes.sql` and `solution/models/intermediate/int_positions_dated.sql`.


## Answer 3: Solution

Read the enriched holdings, join the active-fund attributes for the strategy, group by (fund, date, strategy), and aggregate. The cash slice is a `case` expression inside the `sum`.

```sql
with holdings as (
    select * from {{ ref('int_holdings_enriched') }}
),
funds as (
    select * from {{ ref('int_fund_attributes') }}
)
select
    h.fund_id,
    h.position_date,
    f.strategy_code,
    sum(h.mv_base_ccy)                                    as exposure_base_ccy,
    count(distinct h.instrument_id)                       as instrument_count,
    sum(case when h.instrument_id like 'CASH_%'
             then h.mv_base_ccy else 0 end)               as cash_exposure_base_ccy
from holdings h
left join funds f
    on f.fund_id = h.fund_id
group by 1, 2, 3
```

Reference: `solution/models/marts/agg_fund_exposure.sql`.


## Answer 4: Solution

Roll the enriched holdings up to a per-fund-day total MV in `fund_mv`, divide by a synthesised `units_outstanding` in `with_units`, then join that back to the instrument grain and carry the holding columns plus the fund name.

```sql
with holdings as (
    select * from {{ ref('int_holdings_enriched') }}
),
funds as (
    select * from {{ ref('int_fund_attributes') }}
),
fund_mv as (
    select fund_id, position_date, sum(mv_base_ccy) as total_mv_base
    from holdings
    group by 1, 2
),
with_units as (
    select
        fund_id, position_date, total_mv_base,
        100000000.0 as units_outstanding
    from fund_mv
)
select
    h.fund_id,
    h.position_date,
    h.instrument_id,
    f.fund_name,
    h.quantity,
    h.mv_local_ccy,
    h.local_ccy,
    h.fx_rate_to_base,
    h.mv_base_ccy,
    u.total_mv_base / u.units_outstanding as calc_nav_per_unit
from holdings h
left join with_units u
    on u.fund_id = h.fund_id and u.position_date = h.position_date
left join funds f
    on f.fund_id = h.fund_id
```

Reference: `solution/models/marts/fct_portfolio_returns.sql`.


## Answer 5: Solution

The generic tests are declared by column in `models/marts/schema.yml`. Keys get `not_null`; the fact's `fund_id` gets a `relationships` test against the active-fund model; the aggregate's `strategy_code` gets `accepted_values`.

```yaml
models:
  - name: fct_portfolio_returns
    columns:
      - name: fund_id
        tests:
          - not_null
          - relationships:
              arguments:
                to: ref('int_fund_attributes')
                field: fund_id
      - name: position_date
        tests: [not_null]
      - name: instrument_id
        tests: [not_null]
      - name: mv_base_ccy
        tests: [not_null]

  - name: agg_fund_exposure
    columns:
      - name: fund_id
        tests: [not_null]
      - name: position_date
        tests: [not_null]
      - name: strategy_code
        tests:
          - accepted_values:
              arguments:
                values: ['EQ-LC', 'EQ-EM', 'EQ-GC', 'FI-IG']
```

Reference: `solution/models/marts/schema.yml`.


## Answer 6: Solution

Compare the calculated NAV to the seeded custodian NAV, join on (fund, date), compute the variance in basis points, and return only the rows that breach the 1bp tolerance — so any breach is a test failure.

```sql
with calc as (
    select fund_id, position_date, calc_nav_per_unit
    from {{ ref('fct_portfolio_returns') }}
    where calc_nav_per_unit is not null
),
custodian as (
    select fund_id, position_date, nav_per_unit
    from {{ ref('seed_custodian_nav') }}
),
variance as (
    select
        c.fund_id,
        c.position_date,
        c.calc_nav_per_unit,
        cu.nav_per_unit                                          as custodian_nav,
        (c.calc_nav_per_unit - cu.nav_per_unit) / cu.nav_per_unit * 10000.0
            as variance_bps
    from calc c
    inner join custodian cu
        on cu.fund_id = c.fund_id
        and cu.position_date = c.position_date
)
select * from variance
where abs(variance_bps) > 1.0
```

Reference: `solution/tests/assert_nav_within_tolerance.sql`.


## Answer 7: Solution

`dbt build` loads all eight CSV seeds, builds the five staging views, three intermediate views, and two mart tables in DAG order, then runs every test. A clean run ends with `ERROR=0 SKIP=0`. There is no model SQL for this section; the deliverable is a green full build.

```bash
dbt build
# Done. PASS=N WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=N
```


## Answer 8: Solution

`dbt docs generate` writes the manifest and catalog from your descriptions plus the inferred DAG; `dbt docs serve` renders them. The lineage graph is built entirely from the `source()` and `ref()` calls already in your models — there is nothing extra to author. Click `fct_portfolio_returns` in the served site and the graph traces back through the intermediate and staging layers to the sources.

```bash
dbt docs generate
dbt docs serve --host 127.0.0.1 --port 8081
```

Reference: the graph is generated from `dbt/models/sources.yml` and every
`ref()` across `solution/models/`.


## Answer 9: Solution

The post-hook is a one-line folder-level config on `marts` in `dbt_project.yml`. `{{ this }}` resolves to the mart's own table; dbt runs the `OPTIMIZE` after building each mart. It sits on the `marts` folder so only the mart tables are z-ordered — the staging and intermediate views run nothing.

```yaml
models:
  portfolio_analytics_challenge:
    marts:
      +materialized: table
      +tags: ["marts"]
      +post-hook: "OPTIMIZE {{ this }} ZORDER BY (fund_id, position_date)"
```

Reference: `dbt/dbt_project.yml`.


## Answer 10: Solution

Roll `agg_fund_exposure` up from (fund, date, strategy) to (fund, date), guard the keys with `not_null`, and assert the two totals agree in a singular reconciliation test — the same "prove the rollup lost no money" pattern, applied to your own mart.

`dbt/models/marts/agg_fund_daily_exposure.sql`:

```sql
with strat as (
    select * from {{ ref('agg_fund_exposure') }}
)
select
    fund_id,
    position_date,
    sum(exposure_base_ccy)      as total_exposure_base_ccy,
    sum(cash_exposure_base_ccy) as total_cash_base_ccy
from strat
group by 1, 2
```

Add to `dbt/models/marts/schema.yml`:

```yaml
  - name: agg_fund_daily_exposure
    description: "Per (fund, date) total base-ccy exposure, rolled up from agg_fund_exposure."
    columns:
      - name: fund_id
        tests: [not_null]
      - name: position_date
        tests: [not_null]
```

`dbt/tests/reconcile_daily_exposure.sql`:

```sql
-- Reconciliation: rolling the strategy-level exposure up to (fund, date) must
-- preserve the total. Returns a row (test FAILS) only on drift beyond tolerance.
select
    daily_total,
    strat_total,
    abs(daily_total - strat_total) as diff
from (
    select
        (select sum(total_exposure_base_ccy) from {{ ref('agg_fund_daily_exposure') }}) as daily_total,
        (select sum(exposure_base_ccy)       from {{ ref('agg_fund_exposure') }})       as strat_total
)
where abs(daily_total - strat_total) > 0.01
```

Reference: `solution/models/marts/agg_fund_daily_exposure.sql`, the `agg_fund_daily_exposure` block in `solution/models/marts/schema.yml`, and `solution/tests/reconcile_daily_exposure.sql`.

