# Instructor legacy stretch answers — capstone

Preserved from `challenges/v2/capstone/phase-two-proficient/stretch/README.md` before separation. These legacy exercises retain their separate v1 runtime and access requirements; they are not evidence of v2 live execution. No real notification or external publishing is authorized.
## Answer 1: Solution

Take the per-portfolio AUM/fees/trades/positions straight from `rpt_portfolio_summary`,
re-aggregate `dom_positions__position` to portfolio grain for the buy/sell totals, and
compute the blended rate as `fees_paid * 10000 / nullif(traded_value, 0)`. Multiply first:
on Databricks, dividing two `decimal(38,6)` values keeps only 6 decimal places, so
`fees_paid / traded_value * 10000` rounds the rate to 0.01 bps.

```sql
with positions as (
  select
    portfolio_id,
    sum(total_bought) as buy_value,
    sum(total_sold)   as sell_value
  from {{ ref('dom_positions__position') }}
  group by portfolio_id
)

select
  s.portfolio_id,
  s.aum,
  s.fees_paid,
  s.trades,
  s.positions,
  p.buy_value,
  p.sell_value,
  p.buy_value - p.sell_value as net_flow,
  -- Why: nullif so a zero traded value yields NULL not a div-by-zero error
  s.fees_paid * 10000 / nullif(p.buy_value + p.sell_value, 0) as fee_bps_realized
from {{ ref('rpt_portfolio_summary') }} s
join positions p using (portfolio_id)
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/portfolio_perf/dbt/prepared/rpt_portfolio_performance.sql`.


## Answer 2: Solution

Pass the advisor-book columns through and add the gap-free ranking window.

```sql
-- Advisors ranked by book AUM. dense_rank() so ties share a rank with no gaps.
select
  advisor_id,
  advisor_name,
  region,
  book_aum,
  fees_generated,
  dense_rank() over (order by book_aum desc) as rank
from {{ ref('rpt_advisor_book') }}
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/advisors/dbt/integration/rpt_advisor_leaderboard.sql`.


## Answer 3: Solution

Build the per-day, per-asset-class aggregate in a CTE, then layer the 7-row rolling sum over
it so the window sees one row per `(asset_class, trade_date)`.

```sql
with daily as (
  select
    t.trade_date,
    i.asset_class,
    sum(t.gross_value) as traded_value,
    sum(t.fee)         as fees,
    count(*)           as trades
  from {{ ref('dom_trading__trade') }} t
  join {{ ref('dom_instrument__instrument') }} i using (instrument_id)
  group by t.trade_date, i.asset_class
)

select
  trade_date,
  asset_class,
  traded_value,
  fees,
  trades,
  sum(traded_value) over (
    partition by asset_class
    order by trade_date
    rows between 6 preceding and current row
  ) as rolling_7d_value
from daily
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/market_daily/dbt/prepared/ts_daily_asset_class.sql`.


## Answer 4: Solution

The shipped `sources.yml` already has the correct configuration:

```yaml
tables:
  - name: trades
    config:
      loaded_at_field: "cast(timestamp_seconds(ts) as timestamp)"
      freshness:
        warn_after: {count: 100000, period: day}
        error_after: {count: 200000, period: day}
```

`loaded_at_field` and `freshness` sit under `config:` — that is where dbt expects them from
v1.10 onward.

The thresholds are wide so the historical teaching sample passes. Tighten them to see the
freshness check fire.


## Answer 5: Solution

Three `dashboard` exposures, each owning one upstream consumer-aligned mart.

```yaml
version: 2

exposures:
  - name: advisor_dashboard
    label: "Advisor performance dashboard"
    type: dashboard
    maturity: high
    owner:
      name: Sales Ops
      email: sales-ops@example.com
    depends_on:
      - ref('rpt_advisor_book')

  - name: portfolio_dashboard
    label: "Portfolio executive dashboard"
    type: dashboard
    maturity: high
    owner:
      name: Wealth Analytics
      email: wealth-analytics@example.com
    depends_on:
      - ref('rpt_portfolio_summary')

  - name: market_dashboard
    label: "Market activity dashboard"
    type: dashboard
    maturity: medium
    owner:
      name: Trading Desk
      email: trading-desk@example.com
    depends_on:
      - ref('ts_daily_market')
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/exposures.yml`.


## Answer 6: Solution

Two single-expression macros; `basis_points` interpolates both arguments and divides by 10000.

```sql
{% macro cents_to_decimal(column_name) -%}
  {{ column_name }} / 100.0
{%- endmacro %}


{% macro basis_points(amount_column, bps_column) -%}
  {{ amount_column }} * {{ bps_column }} / 10000.0
{%- endmacro %}
```

Reference: `data_products/atlas_elt/shared/macros/money.sql`.


## Answer 7: Solution

The shipped generic test body (whole file):

```sql
{% test non_negative(model, column_name) %}
-- Generic test: fails when the column holds any negative value.
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
```

Attaching it in a dataset YAML (one example; the same `tests: [non_negative]` pattern repeats
on other money columns):

```yaml
- name: rpt_portfolio_summary
  columns:
    - name: aum
      tests: [non_negative]

- name: rpt_portfolio_performance
  columns:
    - name: aum
      tests: [not_null, non_negative]
    - name: fees_paid
      tests: [non_negative]
```

Reference: `data_products/atlas_elt/tests/generic/non_negative.sql`.


## Answer 8: Solution

Add the `relationships` test alongside `not_null` on `dom_trading__trade.portfolio_id`:

```yaml
- name: dom_trading__trade
  columns:
    - name: portfolio_id
      tests:
        - not_null
        - relationships:
            arguments:
              to: ref('dom_portfolio__portfolio')
              field: portfolio_id
```

Arguments to a generic test nest under `arguments:`; dbt 1.11 deprecates the older top-level
form.

Reference: the `trades.yml` dataset YAML.


## Answer 9: Solution

`tests/reconcile_advisor_book_aum.sql`:

```sql
-- Reconciliation: sum(book_aum) across advisors must equal sum(aum) across portfolios.
-- Returns a row (test FAILS) only when the two totals drift beyond a small tolerance.
select book_total, summary_total, abs(book_total - summary_total) as diff
from (
  select
    (select sum(book_aum) from {{ ref('rpt_advisor_book') }})       as book_total,
    (select sum(aum)      from {{ ref('rpt_portfolio_summary') }})   as summary_total
)
where abs(book_total - summary_total) > 0.01
```

`tests/reconcile_segment_aum.sql`:

```sql
-- Reconciliation: sum(aum) across segments must equal sum(aum) across portfolios.
select segment_total, summary_total, abs(segment_total - summary_total) as diff
from (
  select
    (select sum(aum) from {{ ref('agg_segment_aum') }})             as segment_total,
    (select sum(aum) from {{ ref('rpt_portfolio_summary') }})        as summary_total
)
where abs(segment_total - summary_total) > 0.01
```

Reference: `data_products/atlas_elt/tests/reconcile_advisor_book_aum.sql` and
`data_products/atlas_elt/tests/reconcile_segment_aum.sql`.


## Answer 10: Solution

The same daily aggregate as `ts_daily_market`, plus the incremental `config(...)` and an
`is_incremental()`-guarded `where` filtering to trade dates past the current `max(trade_date)`.

```sql
{{ config(materialized='incremental', unique_key='trade_date') }}

select
  trade_date,
  sum(gross_value) as traded_value,
  sum(fee)         as fees,
  count(*)         as trades
from {{ ref('dom_trading__trade') }}
{% if is_incremental() %}
where trade_date > (select max(trade_date) from {{ this }})
{% endif %}
group by trade_date
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/market_daily/dbt/prepared/ts_daily_market_incremental.sql`.


## Answer 11: Solution

The shipped snapshot (the full body):

```sql
{% snapshot portfolios_snapshot %}
{{
  config(
    target_schema=target.schema,
    unique_key='portfolio_id',
    strategy='check',
    check_cols=['strategy', 'advisor_id']
  )
}}

select
  portfolio_id,
  advisor_id,
  strategy,
  inception_date
from {{ ref('dom_portfolio__portfolio') }}

{% endsnapshot %}
```

Reference: `data_products/atlas_elt/shared/snapshots/portfolios_snapshot.sql`.


## Answer 12: Solution

Roll `rpt_portfolio_summary` up by `region` for the regional mart.

```sql
-- datasets/advisors/dbt/integration/rpt_region_report.sql
select
  region,
  count(*)                  as portfolios,
  count(distinct client_id) as clients,
  sum(aum)                  as aum,
  sum(fees_paid)            as fees_generated
from {{ ref('rpt_portfolio_summary') }}
group by region
```

The reconciliation test (`tests/reconcile_region_aum.sql`) that proves the rollup preserves
total AUM:

```sql
-- Capstone integration proof: regional rollup must preserve total AUM.
-- Returns a row (test FAILS) when the two totals drift beyond tolerance.
select region_aum, summary_aum, abs(region_aum - summary_aum) as diff
from (
  select
    (select sum(aum) from {{ ref('rpt_region_report') }})       as region_aum,
    (select sum(aum) from {{ ref('rpt_portfolio_summary') }})    as summary_aum
)
where abs(region_aum - summary_aum) > 0.01
```

Reference: `challenges/v1/04-atlas-capstone/solution/datasets/advisors/dbt/integration/rpt_region_report.sql`
and `data_products/atlas_elt/tests/reconcile_region_aum.sql`.

**So what: what the marts reveal.** The leaderboard and the regional report make
*concentration* in private wealth visible. A small fraction of advisors run a large share of
the book; AUM clusters into a few regions rather than spreading evenly. Cross-reference
`rpt_portfolio_performance.fee_bps_realized` against client segment and you can see the *fee
inversion*: smaller retail accounts pay a higher fee *rate* (more basis points) than large
institutional accounts, even though the big accounts pay more in absolute money. These are
real structural patterns in wealth management, and they are exactly the kind of finding an
executive dashboard exists to surface. You built the pipeline that lets a manager see them at
a glance, and the reconciliation test is what lets them trust the number.


## Answer 13: Example solution: Atlas Product Discovery and Reverse-Mapping

This is one reasonable response, not the only correct design. It selects
`rpt_portfolio_summary` and `rpt_advisor_book` as its two business-facing outputs.

### Producer–Creator–Consumer Map

| Producer | Contribution | Data Creator | Consumer | Decision |
|---|---|---|---|---|
| Trading and Security Master | Trades, prices, and instrument details | Atlas learner team | Portfolio oversight | Which portfolios hold the most value and require review? |
| Portfolio Administration and CRM | Portfolio, client, and advisor ownership | Atlas learner team | Advisor leadership | Which advisors manage the largest books, and where is AUM concentrated? |

### Consumer-Backwards Map

| Consumer need | Business-facing output | Required sources | Rules and assumptions |
|---|---|---|---|
| Review portfolio value, ownership, activity, and fees | `rpt_portfolio_summary` | `trades`, `instruments`, `portfolios`, `clients`, `advisors` | Keep valid buys and sells, net positions, value them at the latest observed price, then aggregate once per portfolio. |
| Compare advisor books and generated fees | `rpt_advisor_book` | The portfolio summary plus advisor ownership | Each portfolio belongs to one advisor; advisor AUM and fees must reconcile to portfolio totals. |

### Mini-STTM

| Target field | Business meaning | Source field(s) | Transformation in plain English | Check |
|---|---|---|---|---|
| `advisor_name` | Advisor responsible for the portfolio | `portfolios.advisor_id`, `advisors.advisor_id`, `advisors.name` | Follow the portfolio's advisor ID and use the cleaned advisor name. | Every reported portfolio has an advisor. |
| `trade_date` | Calendar date of a trade | `trades.ts` | Convert the epoch timestamp to a date. | Dates are valid and within the sample period. |
| `market_value` | Current estimated value of one portfolio position | Trade quantities and latest instrument price | Net buys and sells, then multiply the resulting quantity by the latest observed price. | Latest price exists and the same position is not counted twice. |
| `aum` | Estimated assets managed for a portfolio | Position market values | Sum position market value once per portfolio. | Total portfolio AUM reconciles with advisor and segment totals. |
| `fees_paid` | Fees generated by a portfolio's valid trades | `trades.qty`, `price_cents`, `fee_bps` | Calculate traded value and apply the fee rate in basis points, then sum by portfolio. | Fees are non-negative and use 10,000 basis points per whole unit. |
| `book_aum` | Total AUM managed by an advisor | Portfolio `aum`, portfolio advisor | Sum portfolio AUM once per advisor. | Total advisor book AUM equals total portfolio AUM within tolerance. |

### Shared Glossary

- **AUM:** the estimated current value of assets being managed, calculated here from net
  positions and latest observed prices.
- **Position:** the net quantity of one instrument held by one portfolio after buys and sells.
- **Latest price:** the price from the newest valid trade for an instrument, with trade ID used
  to resolve equal timestamps.
- **Gross value:** trade quantity multiplied by price before fees.
- **Fee:** gross trade value multiplied by `fee_bps / 10000`.
- **Basis point:** one hundredth of one percent; 10,000 basis points equal 100%.
- **Advisor book:** the clients and portfolio AUM assigned to an advisor.
- **Valid trade:** a buy or sell with a recognised side, positive quantity, and positive price.

### Trust Questions and Assumptions

- Does every valid trade refer to a known portfolio and instrument?
- Are trades counted exactly once across positions and market-activity outputs?
- Do portfolio, advisor, segment, and regional AUM totals reconcile within tolerance?
- How should late-arriving trades affect the latest price and historical daily totals?
- Monetary totals combine currencies without FX conversion, so cross-currency comparisons are
  indicative rather than directly comparable.

