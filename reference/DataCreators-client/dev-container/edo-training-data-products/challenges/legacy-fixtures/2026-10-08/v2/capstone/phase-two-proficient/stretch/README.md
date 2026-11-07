# capstone: optional stretch selection

Legacy extensions3,4,5,6,7,10,11,12,13 remain in v1/04-atlas-capstone (each 30–120 minutes; integration can exceed 120). The complete concepts and exercises below retain their original learner explanations and checks.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

## Full legacy advanced reference

The following complete original advanced route uses **v1** paths and runtime semantics. Core-equivalent topics remain here for teaching coverage; they are not additional v2 core tasks. All fourteen exercises remain available with their explanations, hints and checks.

## 🚀 Phase 2: Advanced Technical Extensions

Phase 1 left you with a running baseline: seeds landed, source-aligned and domain-aligned
products built, a first consumer-aligned mart, and the `atlas_elt` DAG configuration in
place. Phase 2 is optional, advanced capstone work for technical learners who want to design
and build richer consumer-aligned marts, dbt tests, macros, source-freshness and exposure
metadata, incremental models, and snapshots.

Every challenge is self-contained. The shape is always:

- **Concept** — the idea, explained in plain English.
- **Goal** — the business outcome in one line.
- **Authoring task** — exactly what you write, and into which stub file.
- **How to check** — a command or observable result.

The complete set represents 3+ hours of work if pursued in depth. Pick the challenges that
support your team's outcome; they build on each other roughly in order, and Challenge 14 is
the integrative capstone that ties the marts together. You are not expected to finish all 14.

---

### Phase 2 dependency map

All Phase 2 challenges require the completed Phase 1 MVP. Most can then be attempted
independently; use this map before choosing one:

| Challenge | Additional prerequisite | Why |
|---|---|---|
| 1. Portfolio performance | None | Uses Phase 1 portfolio summary and positions |
| 2. Advisor leaderboard | None | Uses the Phase 1 advisor book |
| 3. Asset-class activity | None | Uses Phase 1 trades and instruments |
| 4. Source freshness | None | Uses the existing `trades` source declaration |
| 5. Exposures | None | Documents consumers of Phase 1 marts |
| 6. Money macro | None | Reviews macros already used by Phase 1 trades |
| 7. Non-negative test | None | Applies a test to Phase 1 money columns |
| 8. Relationship test | None | Connects Phase 1 trades and portfolios |
| 9. Reconciliation tests | None | Compares Phase 1 mart totals |
| 10. Incremental mart | None | Rebuilds the Phase 1 daily-market logic incrementally |
| 11. Portfolio snapshot | None | Snapshots the Phase 1 portfolio model |
| 12. Extend orchestration | Section 8 Airflow inspection | Builds on the rendered DAG workflow |
| 13. Params-driven orchestration | Section 8 Airflow inspection | Traces runtime values through the bundle job |
| 14. Regional capstone | Challenge 2 required; Challenge 9 recommended | Builds the leaderboard and applies the reconciliation pattern |

Before running any Phase 2 dbt command, return to the project:

```bash
cd /workspaces/edo-training-data-products/data_products/atlas_elt
```

---

### Challenge 1: A richer executive report mart

#### Concept

The Phase 1 `rpt_portfolio_summary` answers "what is each portfolio worth?" An
executive wants more in one place: how much was traded, how much flowed in versus out, and
what fee rate the client actually paid. Fees are stored in basis points (bps), where one
basis point is 0.01% of the traded value. Different trades carry different bps, so the
*blended* rate a portfolio actually paid is the total fees divided by the total traded value,
expressed back in basis points: `fees_paid / traded_value * 10000`. This is `fee_bps_realized`.

#### Goal

One mart an executive can read to see AUM, fees, trading volume, net flow, and the
realised fee rate per portfolio.

#### Task

Complete the stub at
`data_products/atlas_elt/datasets/portfolio_perf/dbt/prepared/rpt_portfolio_performance.sql`,
one row per portfolio with: `aum`, `fees_paid`, `trades`, `positions`, `buy_value`,
`sell_value`, `net_flow` (buys minus sells), and `fee_bps_realized`. The AUM, fees, trades,
and positions counts are already rolled up in `ref('rpt_portfolio_summary')`. The buy and sell
values come from `total_bought` and `total_sold` in `ref('dom_positions__position')`, which
is at portfolio/instrument grain — re-aggregate to portfolio grain first. Guard the fee-rate
division against a zero traded value.

#### Check

```bash
dbt build --select rpt_portfolio_performance
dbt show --select rpt_portfolio_performance --limit 5
```

The `fee_bps_realized` values should be in a believable range (low single digits to low tens
of bps), not zero and not thousands. If a portfolio shows a wild number, your denominator
is wrong.

Docs: [dbt marts](https://docs.getdbt.com/best-practices/how-we-structure/4-marts),
[dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 2: Advisor leaderboard with `dense_rank()`

#### Concept

A *window function* computes a value across a set of rows related to the current
row, without collapsing them the way `group by` does. Ranking is the classic case. SQL gives
you three ranking functions that differ in how they treat ties:

- `row_number()` gives every row a distinct number, even on a tie.
- `rank()` gives tied rows the same rank but then *skips* the next number.
- `dense_rank()` gives tied rows the same rank and does *not* skip — ties share a position,
  the ranking stays gap-free.

For a leaderboard you usually want `dense_rank()`: "rank 5" always means the fifth distinct
AUM level. You write it as `dense_rank() over (order by book_aum desc)`.

#### Goal

A leaderboard a sales manager can read top-down: advisors ordered by the size of
the book they run.

#### Task

Complete the stub at
`data_products/atlas_elt/datasets/advisors/dbt/integration/rpt_advisor_leaderboard.sql`.
Select from `ref('rpt_advisor_book')` (which carries `advisor_id`, `advisor_name`, `region`,
`book_aum`, `fees_generated`) and add a `rank` column computed with `dense_rank()` ordered
by `book_aum` descending.

#### Check

```bash
dbt build --select rpt_advisor_leaderboard
dbt show --select rpt_advisor_leaderboard --limit 10
```

Rank 1 should be the largest `book_aum`. If you have ties, confirm they share a rank and the
next rank is not skipped. Try swapping `dense_rank()` for `rank()` to see the gap behaviour
change.

Docs: [dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 3: Daily activity by asset class, plus a rolling window

#### Concept

The Phase 1 `ts_daily_market` totals trading per day across everything. Two
refinements make it analyst-grade. First, *break it down by asset class* (Equity, Bond, ETF,
Commodity) so you can see which kinds of instruments drove a given day. That needs a join to
`dom_instrument__instrument` and a `group by trade_date, asset_class`. Second, add a *rolling
window*. A window function can run a calculation over a sliding *frame* of rows defined by a
`rows between` clause. A 7-day rolling sum is
`sum(traded_value) over (... rows between 6 preceding and current row)`: the current row plus
the six before it. The `partition by asset_class` keeps each asset class's window separate;
`order by trade_date` defines what "preceding" means.

#### Goal

A daily activity mart split by asset class, with a 7-day rolling traded-value
column for trend-spotting.

#### Task

Complete the stub at
`data_products/atlas_elt/datasets/market_daily/dbt/prepared/ts_daily_asset_class.sql`. Start
from `ref('dom_trading__trade')` joined to `ref('dom_instrument__instrument')`, group by
`trade_date` and `asset_class`, and produce `traded_value`, `fees`, and `trades` per group.
Then add `rolling_7d_value`: a window sum of `traded_value` over a 7-row frame, partitioned
by `asset_class` and ordered by `trade_date`.

#### Check

```bash
dbt build --select ts_daily_asset_class
dbt show --select ts_daily_asset_class --limit 20
```

For any asset class, on the earliest dates the rolling value equals the running sum (fewer
than 7 days exist yet); once seven days have passed it tracks a 7-day total.

Docs: [dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 4: Declare source freshness on the source extracts

#### Concept

A dbt **source** is a named pointer to tables that dbt did not build. Declaring
sources lets dbt run freshness checks: you tell dbt which column carries the load timestamp
(`loaded_at_field`) and how old is too old (`freshness` thresholds: `warn_after` and
`error_after`). Then `dbt source freshness` queries `max(loaded_at_field)`, compares it to
now, and reports fresh/warn/error per source table. In a real pipeline this catches an
upstream feed that silently stopped delivering before stale data poisons every downstream
mart. The freshness config lives as metadata on the source declaration in
`data_products/atlas_elt/datasets/sources.yml`.

#### Goal

Make dbt able to tell you, on demand, whether the source `trades` extract is recent
enough to trust.

#### Task

The `sources.yml` already ships with a freshness block on the `trades`
table — it uses `cast(timestamp_seconds(ts) as timestamp)` as the `loaded_at_field` (the
trade's `ts` epoch second serves as the load timestamp for this exercise) and deliberately
wide day-based thresholds so the historical sample reports `pass`/`warn`. Inspect
`data_products/atlas_elt/datasets/sources.yml` to read the existing configuration, then:

1. Confirm the `loaded_at_field` expression is valid by running the freshness check.
2. Temporarily tighten the `warn_after` threshold to `{count: 1, period: day}` and re-run to
   watch the historical data flip to `warn`, then restore the original wide value.

#### Check

```bash
dbt source freshness
```

With the shipped wide thresholds, `trades` should report `pass` or `warn`.

Docs: [dbt source freshness](https://docs.getdbt.com/reference/resource-properties/freshness),
[dbt sources](https://docs.getdbt.com/docs/build/sources)

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 5: Document who consumes the marts with exposures

#### Concept

A dbt **exposure** is a declared downstream *consumer* of your models: a
dashboard, a report, an application, a notebook. It is metadata, not a model — it does not
build anything. You declare it in a YAML file, naming the models it `depends_on`, an owner,
and a type. Exposures appear in `dbt docs` and the lineage graph, so anyone can see which
marts feed which dashboards. You can also select on them:
`dbt build --select +exposure:advisor_dashboard` builds everything that dashboard depends on.

#### Goal

Make the dependency from business-facing dashboards back to the consumer-aligned
marts explicit and queryable.

#### Task

Create `data_products/atlas_elt/datasets/exposures.yml`. Declare at least
three exposures (an advisor dashboard, a portfolio dashboard, and a market-activity
dashboard), each with a `name`, a `type` (`dashboard`), an `owner` (name and email), and a
`depends_on` list written as `ref('...')` naming the consumer-aligned mart that feeds it.

#### Check

```bash
dbt parse
dbt ls --select +exposure:advisor_dashboard
```

`dbt parse` succeeds if the YAML is valid. The `dbt ls` line should list the advisor marts
(and their upstreams) that the exposure depends on. It also lists the `reconcile_*` singular
tests attached to those marts — `dbt ls` returns every resource type unless you narrow it,
so add `--resource-type model` if you want just the models.

Docs: [dbt exposures](https://docs.getdbt.com/docs/build/exposures),
[exposure properties](https://docs.getdbt.com/reference/exposure-properties)

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 6: A reusable money macro

#### Concept

A dbt **macro** is a reusable snippet of SQL-generating logic, written in Jinja,
that you call from models so a calculation is defined once and used everywhere. You have
already used one: `{{ epoch_date('ts') }}` in `dom_trading__trade` expands to the
date-conversion SQL. The money calculations in this project repeat: prices are stored as
integer cents and must be divided by 100, and fee rates are stored in basis points and must
be divided by 10000. Wrapping them in macros (`cents_to_decimal`, `basis_points`) means the
conversion is named, consistent, and changed in one place.

#### Goal

Define money conversions once so every model uses the same named logic instead of
scattered magic numbers.

#### Task

This one is reading, not writing. `shared/` is a local dbt *package*
shared across data products, so it ships complete and sits outside this challenge's reset
scope — there is no `TODO` in it to replace. Open
`data_products/atlas_elt/shared/macros/money.sql` and read both macros:
`cents_to_decimal(column_name)` returns `column_name / 100.0`, and
`basis_points(amount_column, bps_column)` returns `amount_column * bps_column / 10000.0`
(one basis point is 1/10000). Then find where they are already called — `epoch_date` and
`cents_to_decimal` in `dom_trading__trade`, and `basis_points` where a fee is applied — and
satisfy yourself that no model computes `/ 100.0` or `/ 10000.0` by hand. That is the point
of the macro: the conversion is named once and changed in one place.

#### Check

```bash
dbt compile --select dom_trading__trade
```

Open the compiled file and confirm your `{{ cents_to_decimal(...) }}` call expanded to
`price_cents / 100.0`. Then `dbt build --select dom_trading__trade` to confirm the model
still produces the same numbers.

Docs: [dbt Jinja and macros](https://docs.getdbt.com/docs/build/jinja-macros)

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 7: A custom generic test for non-negative money

#### Concept

dbt tests are assertions that pass when a query returns zero rows. A **generic
test** is one you can attach to any column by name, the way `not_null` and `unique` work. You
write it once as a parametrised query in the `tests/generic/` folder, taking `model` and
`column_name`, and selecting the *bad* rows (those that violate the rule). A natural one for
this project is `non_negative`: money columns like AUM, fees, and traded value should never
go below zero — a negative value almost always means a join fanned out or a sign flipped
upstream. Because it is generic, one definition guards every money column you point it at.

#### Goal

One reusable assertion that flags any negative value in any money column you attach
it to.

#### Task

Two parts. First, the generic test already ships in
`data_products/atlas_elt/tests/generic/non_negative.sql` — inspect it to understand the
`{% test non_negative(model, column_name) %}` shape. Second, *apply* it by adding
`non_negative` to money columns in the dataset YAML files (e.g. `aum` in the `advisors.yml`
file under `rpt_portfolio_summary`).

> **Stuck? Try Copilot.** Ask: "In this dbt project, show me how to attach the existing
> `non_negative` generic test to `rpt_portfolio_summary.aum`. Explain the YAML change, but do
> not edit any files." Review the suggested model and column names before applying it.

#### Check

```bash
dbt test --select rpt_portfolio_summary --indirect-selection=cautious
```

Each attached column produces a `non_negative_<model>_<column>` test that should PASS. To
prove it bites, temporarily attach it to `signed_qty` in `dom_trading__trade` (sell trades are
negative) and watch it FAIL, then remove that line.

> `--indirect-selection=cautious` for the same reason as Section 7: `rpt_portfolio_summary`
> is an input to `reconcile_region_aum`, which also reads `rpt_region_report` — a mart you do
> not write until Challenge 14. Without the flag dbt's default `eager` mode runs that test
> too, it fails on the still-stubbed mart, and the command exits non-zero for a reason that
> has nothing to do with the test you just wrote. Drop the flag once Challenge 14 is done.

Docs: [writing custom generic tests](https://docs.getdbt.com/best-practices/writing-custom-generic-tests),
[dbt data tests](https://docs.getdbt.com/docs/build/data-tests)

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 8: A relationship (referential-integrity) test

#### Concept

A **relationships test** is dbt's built-in check for referential integrity: it
asserts that every value in a foreign-key column exists as a key in another model — the dbt
equivalent of a foreign-key constraint. You declare it in a dataset YAML on the child column,
naming the parent model (`to: ref('...')`) and the parent key (`field: ...`). dbt fails the
test if any child row points at a key the parent does not have (an *orphan*). This matters
because of how AUM is built: `rpt_portfolio_summary` joins trades to portfolios. If
`dom_trading__trade.portfolio_id` contains an id with no matching portfolio, that trade's
value is silently dropped by the join, and the firm's reported AUM is quietly understated. A
relationships test turns that silent loss into a loud test failure.

#### Goal

Prove that every trade points at a real portfolio, so no trade value goes missing in
the AUM rollup.

#### Task

In the `trades` dataset YAML (`datasets/trades/dbt/trades.yml`), under
`dom_trading__trade`, add a `relationships` test on `portfolio_id` with
`to: ref('dom_portfolio__portfolio')` and `field: portfolio_id`.

#### Check

```bash
dbt test --select dom_trading__trade
```

The generated `relationships_dom_trading__trade_portfolio_id__...` test should PASS, confirming
no orphan portfolio ids.

Docs: [dbt data tests](https://docs.getdbt.com/reference/resource-properties/data-tests)

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 9: Singular reconciliation tests within tolerance

#### Concept

A **singular test** is a single hand-written SQL file in `tests/` that fails
when its query returns any rows. Unlike a generic test, it is not attached to a column; it
tests one specific assertion across whatever models you reference. The powerful case is
*reconciliation*: two marts roll the same money up different ways, so their totals must agree.
`rpt_advisor_book` sums AUM by advisor; `rpt_portfolio_summary` sums it by portfolio. Because
every portfolio has exactly one advisor, `sum(book_aum)` across advisors must equal
`sum(aum)` across portfolios. You compare the two totals and return a row only when they
differ by more than a small **tolerance** (for floating-point rounding). A reconciliation
test proves a rollup did not lose or double-count money.

#### Goal

Prove the advisor and segment rollups preserve total AUM, so the firm reports one
consistent number however it is sliced.

#### Task

Before opening the shipped tests, choose one route to describe the
advisor-book reconciliation:

1. **Manual route:** write the invariant, the two totals being compared, and the tolerance in
  plain English, then sketch the SQL that should return only mismatches.
2. **Copilot route:** use the prompt below to generate a draft, then identify its two `ref()`
  calls, tolerance, and failure condition.

> **Try with Copilot.** "Draft a dbt singular reconciliation test comparing total
> `rpt_advisor_book.book_aum` with total `rpt_portfolio_summary.aum`. It must return a row only
> when the totals differ by more than 0.01. Explain why zero returned rows means PASS. Do not
> edit files."

Now inspect `tests/reconcile_advisor_book_aum.sql` and `tests/reconcile_segment_aum.sql`.
Compare the shipped implementation with your manual sketch or Copilot draft. Then:

1. Run both tests to confirm they pass on the data you built.
2. Temporarily change the tolerance to a negative number so any tiny drift trips it,
   confirm it fails, then restore it.

A third reconciliation, `tests/reconcile_trade_counts.sql`, ships alongside them and runs on
every `dbt build`/`dbt test`, so you will see it in the output. It checks a *count* rather
than a money total: every valid trade must be counted exactly once in
`dom_positions__position`, `ts_daily_market` and `agg_instrument_activity`, so
`sum(trades)` has to agree across all three. It needs no tolerance — counts are exact, and
any disagreement means a join dropped or duplicated rows.

#### Check

```bash
dbt test --select reconcile_advisor_book_aum reconcile_segment_aum
```

Both should PASS (return zero rows).

Docs: [dbt singular data tests](https://docs.getdbt.com/docs/build/data-tests)

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 10: An incremental market mart

#### Concept

By default a dbt model is fully rebuilt every run. For a small classroom dataset
that is fine, but a real daily-market table grows forever and rebuilding all history every
night is wasteful. An **incremental** model rebuilds only the new rows. You set
`materialized='incremental'` and give dbt a `unique_key`. On the first run it builds
everything. On later runs, the `is_incremental()` block adds a `where` clause that filters to
only rows newer than what is already in the table: `where trade_date > (select max(trade_date)
from {{ this }})`, where `{{ this }}` is the model's own existing table. `unique_key` lets
dbt replace a row if the same key reappears, so a re-run of yesterday updates rather than
duplicates.

#### Goal

A daily-market mart that, after its first build, only processes new trade dates
instead of rebuilding all of history.

#### Task

Complete the stub at
`data_products/atlas_elt/datasets/market_daily/dbt/prepared/ts_daily_market_incremental.sql`.
It produces the same daily aggregates as `ts_daily_market` (traded value, fees, trades,
grouped by `trade_date`), but configured `materialized='incremental'` with
`unique_key='trade_date'` and an `is_incremental()` filter that only selects trade dates
later than the current `max(trade_date)` in the table.

> **Required AI Catalyst checkpoint.** In Copilot Chat, ask: "Use the dbt best practices
> skill to review the models in `data_products/atlas_elt`. Which models are reasonable
> candidates for incremental materialization, and why? Analyse only; do not edit files."
> Compare its recommendation with `ts_daily_market_incremental`. Check that it discusses
> table growth, a reliable date or key, late-arriving data, and the cost of rebuilding. The
> Catalyst interaction informs your decision; the dbt commands below remain the acceptance
> check.

#### Check

```bash
dbt build --select ts_daily_market_incremental
# Run it a second time:
dbt run --select ts_daily_market_incremental
```

On the second run dbt appends rather than rebuilding, because no trade dates are newer than
what is already there. Note that the terminal text is **identical** both times
(`OK created sql incremental model ...`) — dbt prints no row count or incremental marker, so
there is nothing visual to compare. To actually see the difference, read the compiled SQL:

```bash
# This project normally writes artifacts to a Unity Catalog Volume, which is not mounted in
# the devcontainer. Override target-path for this inspection and clean it up afterwards:
TARGET=$(mktemp -d)
dbt compile --select ts_daily_market_incremental --target-path "$TARGET"
find "$TARGET/compiled" -name ts_daily_market_incremental.sql -exec grep -A3 "trade_date >" {} +
rm -rf "$TARGET"
```

Read the `compiled/` copy, not `run/`: for this Databricks `insert_overwrite` incremental
strategy the `run/` artifact is only the `insert overwrite table ... select * from ...__dbt_tmp`
wrapper, so the filter you are looking for appears only in `compiled/`.

The second run's version carries the `where trade_date > (select max(trade_date) ...)` filter
that the first run — which had no table to compare against — did not. Use `--full-refresh` to
rebuild the whole table when needed.

Docs: [dbt incremental models](https://docs.getdbt.com/docs/build/incremental-models),
[unique_key](https://docs.getdbt.com/reference/resource-configs/unique_key)

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 11: A snapshot for slowly-changing portfolios

#### Concept

Dimension data changes over time: a portfolio's strategy is re-classified, or it
is reassigned to a different advisor. A plain model only ever holds the *current* state, so
last night's value overwrites last week's, and the history is gone. A dbt **snapshot**
captures that history. It is a special kind of model defined in the `snapshots/` folder: on
each run it compares the source rows to what it has stored and, when a tracked value has
changed, *closes* the old record and *opens* a new one, recording validity ranges in
`dbt_valid_from` / `dbt_valid_to` columns. This is **slowly-changing-dimension (SCD) type 2**.

**CG paved-path bridge.** This generic `dbt snapshot` teaches the SCD2 *concept*. In
production at CG, slowly-changing history is not `dbt snapshot`; it is the caspian-core
`bitemporal_load_v2` incremental strategy, which emits the `dl_*` audit canon via
`get_audit_cols()` (`dl_business_from_date` / `dl_business_to_date` / `dl_system_from_date` /
`dl_system_to_date`, `dl_row_uid`): bitemporal, richer than the single validity range here.
Rough mapping: `dbt_valid_from` / `dbt_valid_to` ≈ `dl_business_from_date` /
`dl_business_to_date`. Keep the generic snapshot below as the lab artefact.

#### Goal

Keep a full history of portfolio strategy and advisor assignments, so you can
reconstruct the book as it stood on any past date.

#### Task

The snapshot ships at
`data_products/atlas_elt/shared/snapshots/portfolios_snapshot.sql`. Inspect it to understand
the `{% snapshot %}` block structure, then run it:

```bash
dbt snapshot
```

The log should say it snapshotted `portfolios_snapshot`. The physical snapshot table also has dbt-managed
`dbt_valid_from`, `dbt_valid_to`, and `dbt_scd_id` columns. On a first run every row is open
(`dbt_valid_to` is null). Run `dbt snapshot` again with no source change and the row count
stays the same: snapshots only add rows when a tracked value actually changes.

#### Check

Confirm the snapshot command built and `dbt show` can preview the snapshot
input rows:

```bash
dbt show --select portfolios_snapshot --limit 5
```

Docs: [dbt snapshots](https://docs.getdbt.com/docs/build/snapshots),
[check_cols](https://docs.getdbt.com/reference/resource-configs/check_cols)

Worked answer 11 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 12: Understand and extend the orchestration

#### Concept

The `atlas_elt` product ships per-dataset `*.dag.yml` orchestration files. Each
YAML configures an Airflow DAG that wraps the Databricks bundle job for that dataset. This is
the **CG paved-path orchestration model**: Airflow holds the schedule and Databricks Jobs
executes the dbt run. A `@task.bash` TaskFlow approach (where each Airflow task runs a shell
command like `dbt run --select tag:consumer-aligned`) is a valid teaching pattern, but the
paved path delegates to a Databricks job for scalability and observability at production.

#### Goal

Understand how the paved-path DAG YAML wires to the Databricks job, and where you
would extend it to add a new dataset's DAG.

#### Task

Read the existing DAG YAMLs and answer these questions:

```bash
cat datasets/advisors/airflow/advisors.dag.yml
cat datasets/portfolio_perf/airflow/portfolio_perf.dag.yml
```

1. What schedule does each dataset's DAG use?
2. Which Databricks bundle job name does the DAG trigger?
3. If you added a brand-new consumer mart in a new dataset folder, what file would you
   create to give it an Airflow DAG?

#### Check

Confirm the set of DAG YAMLs matches the set of dataset folders:

```bash
ls datasets/*/airflow/*.dag.yml
```

---

### Challenge 13: Understand params-driven orchestration

#### Concept

Airflow **params** let you parametrise a DAG run: the operator passes a config
dict at trigger time, and tasks read it via `{{ params.<name> }}`. This turns one DAG into a
flexible tool — a `selector` param lets an operator build only `tag:consumer-aligned` instead
of everything; a `run_tests` flag lets them skip the test stage. In the paved path, the
Databricks bundle job can similarly accept `--vars` at run time, overriding catalog, schema,
or dbt vars.

#### Goal

Understand how a run-time parameter flows from the Airflow trigger form through to
the dbt command that executes on Databricks.

#### Task

Inspect the `variables_dev.yml` for the Atlas product:

```bash
cat variables/variables_dev.yml
```

Then look at how a bundle job references variables:

```bash
cat datasets/advisors/bundle/advisors.job.yml
```

Answer:
1. Which variables can be overridden at run time?
2. How would you run only the `advisors` dataset's dbt models via the CLI?
3. What is the analogy between `{{ params.selector }}` in a Python TaskFlow DAG and variable
   overrides in the bundle job?

#### Check

Trace one variable from `variables/variables_dev.yml` into the advisor job file and explain
which value changes without changing the DAG structure.

---

### Challenge 14: A reconciling regional report (capstone)

This challenge ties the rest together. Earlier challenges each added one feature; here you
compose them into an integrated deliverable and *prove it is correct*. The integration proof
is reconciliation: a new rollup must agree, to the penny within tolerance, with the summary it
derives from.

#### Concept

A regional report rolls the whole book up by advisor `region`. The correctness
question is whether that rollup preserves total AUM. If you build `rpt_region_report` from
`rpt_portfolio_summary` (which already carries each portfolio's `region`), then
`sum(aum)` across regions must equal `sum(aum)` across portfolios — no money created and
none lost. The reconciliation singular test asserts exactly that, within a small tolerance, and
returns rows only on a mismatch. The test already ships at
`data_products/atlas_elt/tests/reconcile_region_aum.sql`; your job is to build the mart it
validates, and to confirm the integration proof passes.

#### Goal

A regional AUM report that is provably consistent with the portfolio summary,
enforced by an orchestrated reconciliation test.

#### Task

Two pieces:

1. Complete `data_products/atlas_elt/datasets/advisors/dbt/integration/rpt_region_report.sql`:
   per advisor `region`, the columns `portfolios`, `clients`, `aum`, `fees_generated`, built
   from `ref('rpt_portfolio_summary')`.
2. Inspect `data_products/atlas_elt/tests/reconcile_region_aum.sql` to understand the
   reconciliation pattern, then run it against the mart you built.

#### Check

```bash
dbt build --select rpt_region_report rpt_advisor_leaderboard
dbt test --select reconcile_region_aum
```

`reconcile_region_aum` PASS is the integration proof. The final verification section explains
the difference between offline compilation and a live end-to-end check.

Docs: [dbt singular data tests](https://docs.getdbt.com/docs/build/data-tests),
[dbt exposures](https://docs.getdbt.com/docs/build/exposures)

Worked answer 12 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Use the product

Building tables is not the outcome; helping someone make a decision is. Run at least the
Phase 1 query below, then explain one finding supported by the rows you see.

Run from `data_products/atlas_elt`:

```bash
dbt show --inline "select segment, clients, portfolios, aum from {{ ref('agg_segment_aum') }} order by aum desc" --limit 10
```

If you completed Challenge 14, also inspect the regional report:

```bash
dbt show --inline "select region, portfolios, clients, aum, fees_generated from {{ ref('rpt_region_report') }} order by aum desc" --limit 10
```

> **Turn results into a decision.** Paste the displayed rows into Copilot Chat and ask:
> "Using only these Atlas query results, draft a four-bullet briefing. State one supported
> finding, the intended consumer, a decision that consumer could make, and one caveat or
> follow-up question. Do not invent values or facts not present in the rows."

Check every number in the response against your query output. The intended consumer might be
a sales manager, advisor lead, trading desk, or product owner. A possible decision is where
to investigate concentration, service coverage, or unusual activity next.

The pipeline standardises currency-code spelling but does not perform FX conversion. Monetary
totals combine USD, EUR, GBP, CHF, JPY, and HKD, so treat cross-currency comparisons as
indicative and include that limitation in your briefing.

PDF generation and scheduled email delivery are useful follow-on products, but they require
additional rendering, access-control, and delivery design and are outside this capstone.

---

## Appendix: Quick Reference and Opening Team Activity Example

### Working in the Devcontainer

Run repository commands inside the VS Code devcontainer, not in a terminal on your host machine.
The tools and environment settings used by this capstone are installed in the container.

#### Know where to run commands

| Command type | Directory |
|---|---|
| `mise run ...`, `astro dev ...`, and challenge verification | Repository root |
| `dbt ...` | `data_products/atlas_elt` |

```bash
# Repository root
cd /workspaces/edo-training-data-products

# Atlas dbt project
cd /workspaces/edo-training-data-products/data_products/atlas_elt

# Show your current directory
pwd
```

#### Essential dbt commands

Run these from `data_products/atlas_elt`:

```bash
# Confirm that dbt can connect
dbt debug

# Install project packages
dbt deps

# List models without building them
dbt ls --resource-type model

# Build one model and its upstream dependencies without tests on unfinished models
dbt build --select +rpt_portfolio_summary --indirect-selection=cautious

# Build one alignment
dbt run --select tag:source-aligned

# Preview model results
dbt show --select rpt_portfolio_summary --limit 10

# Test one model without pulling in tests that depend on unfinished models
dbt test --select rpt_portfolio_summary --indirect-selection=cautious
```

In a selector, `+model_name` includes upstream dependencies, `tag:name` selects resources with
that tag, and `--indirect-selection=cautious` runs a test only when all its inputs are selected.
Start with the smallest relevant model or selector instead of rebuilding everything.

#### Databricks connection

Check the profile from the repository root:

```bash
mise exec -- databricks auth describe --profile DEFAULT
```

Then check the dbt connection from `data_products/atlas_elt`:

```bash
dbt debug
```

Do not assume every connection failure requires another login. If the profile cannot mint a valid
token, return to the repository root and run:

```bash
mise run setup:databricks
```

Never paste access tokens, passwords, or other credentials into chat, source files, or commands
that will be retained in shell history.

#### Airflow quick reference

Run these from the repository root:

```bash
astro dev start
astro dev run dags list-import-errors
astro dev run dags list | grep atlas_elt
astro dev run dags details atlas_elt_advisors
astro dev stop
```

Use the Airflow URL printed by `astro dev start`; do not assume it uses port 8080. Configure
Databricks before starting Astro so its containers receive the connection settings. Stop Astro
when you finish to release local memory.

#### Verification commands

Run these from the repository root:

```bash
# Fast dependency, parsing, compilation, and bundle gate
mise run challenge:verify 04

# Phase 1 live gate
CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp mise run challenge:verify 04

# Full live gate after the Phase 2 models are complete
CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04

# Non-destructive instructor overview
challenges/v1/04-atlas-capstone/verify.sh --review
```

The following command is for maintainers only. It deliberately resets the learner tree before
replaying the complete capstone:

```bash
# MAINTAINERS ONLY: destructive to learner work
challenges/v1/04-atlas-capstone/verify.sh --from-scratch
```

#### Starting over

> **Warning:** This command deletes your authored challenge files under
> `data_products/atlas_elt/datasets/`. Run it only when you intend to discard that work.

```bash
mise run challenge:reset 04
```

The reset restores files only. It does not delete tables or views left in your Databricks schema,
so rebuild the relevant models before trusting a test result from a new attempt.

#### Where to find things

| What | Path |
|---|---|
| Learner model files | `data_products/atlas_elt/datasets/` |
| dbt logs | `data_products/atlas_elt/logs/dbt.log` |
| Starter templates | `challenges/v1/04-atlas-capstone/stubs/` |
| Solved references | `challenges/v1/04-atlas-capstone/solution/` |
| Maintainer run evidence | `.devcontainer/verify/04-atlas-capstone/` |

#### Common problems

| Symptom | First action |
|---|---|
| dbt cannot find the project | Run `cd /workspaces/edo-training-data-products/data_products/atlas_elt`. |
| Databricks authentication fails | Run the profile and token-delivery checks in Troubleshooting before logging in again. |
| `No models match` | Confirm you edited `data_products/atlas_elt/`, not `stubs/`. |
| An unfinished model triggers an unrelated test | Add `--indirect-selection=cautious` to the focused command. |
| Atlas DAGs do not appear | Run `astro dev run dags list-import-errors`, then restart Astro. |
| Airflow has old connection settings | Stop Astro, rerun Databricks setup, then start Astro again. |
| You need to inspect generated SQL | Use the temporary `--target-path` pattern from Challenge 10. |
| You are unsure what changed | From the repository root, run `git status --short`. |

#### Safe working habits

- Edit challenge work only under `data_products/atlas_elt/`; never edit `stubs/`.
- Run one dbt command at a time and build the smallest relevant selection first.
- Read the first real error, not only the final summary.
- Run `git status --short` regularly so generated or unexpected changes are visible.
- Do not commit logs, generated targets, credentials, or maintainer verification evidence.
- Do not reset unless you intend to discard your authored work.

### Opening Team Activity Example

Worked answer 13 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Glossary

**Grain** — what one row represents, such as one trade or one portfolio.

**Materialization** — how dbt stores a model, such as a view, table, or incremental table.

**Source** — a table dbt reads but does not build; `source()` records that dependency.

**`ref()`** — a dbt function that names another model and adds it to the dependency graph.

**Natural key** — a real-world identifier already present in the data, such as `trade_id`.

**Window function** — a calculation across related rows without collapsing them into one row.

**Generic test** — a reusable parameterised assertion attached to a model or column.

**Singular test** — a purpose-built SQL query that passes when it returns zero failing rows.

**Reconciliation** — checking that totals agree when the same measure is rolled up differently.

**Incremental model** — a model that processes new or changed rows after its first build.

**Unique key** — the column or columns dbt uses to identify the same row across incremental runs.

**Snapshot / SCD2** — history that preserves old and new versions of a changing record with
validity dates; SCD2 means slowly changing dimension type 2.

---

## Troubleshooting

**`dbt debug` cannot connect.** Do not assume you need to log in again. From the repository
root, first prove whether the existing OAuth profile can mint a token:

```bash
mise exec -- databricks auth describe --profile DEFAULT
mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json >/dev/null' && echo "OAuth token: OK"
mise exec -- sh -c 'test -n "${DBT_ACCESS_TOKEN:-}" && test "$DBT_ACCESS_TOKEN" != "MISSING_run__mise_run_setup_databricks"' && echo "dbt token delivery: OK"
```

If the second command fails with a login or expiry error, run `mise run setup:databricks` and
complete OAuth. If it succeeds but the third command fails, authentication is healthy and
delivery is the problem: run `mise run setup:mise`, open a new terminal, return to the repo,
and retry `dbt debug`. Do not re-authenticate a working profile.

**`No models match tag:source-aligned`** (or `domain-aligned`/`consumer-aligned`). The stubs
are still placeholders, or you have not authored that alignment yet. Complete the model files
for that alignment first, then re-run the `--select tag:...` command.

**`dbt seed` fails on types.** Confirm each CSV in
`data_products/atlas_elt/seeds/` still has its header row and that the `+column_types` in
`dbt_project.yml` match the columns.

**Model produces different row count than expected.** For `dom_trading__trade`, a lower row
count than `src_trading__trades` is correct and expected — the quality filter drops bad trades.
For consumer marts, confirm all `ref()` calls resolve to the domain-aligned products, not
directly to source-aligned stubs.

**Want to start over.** The following command deletes your authored challenge work and copies
the placeholder templates back into the product. Run it only when you explicitly want that:

```bash
mise run challenge:reset 04
```

## Verify your work

Run the fast verification gate from the repository root:

```bash
mise run challenge:verify 04
```

An `OFFLINE PASS` means dbt dependencies, parsing, compilation, and the available bundle
validation completed. It does **not** mean models or tests ran on Databricks, and the output
says so explicitly. The gate restores `package-lock.yml`, so it does not leave that generated
file dirty.

To verify only the required Phase 1 MVP live, use the completion command from
**Complete Phase 1**:

```bash
CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp mise run challenge:verify 04
```

After completing Challenge 14, run the live completion gate:

```bash
CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04
```

A `LIVE PASS` means the models ran and all dbt tests passed on Databricks. Only this mode
prints `Atlas ELT capstone complete.` Bundle deployment is a separate operational action; it
is not required to prove your dbt work is correct.

### Maintainer-only from-scratch verification

Maintainers can reproduce the full learner journey, including all optional Phase 2 challenges,
from a reset starter tree:

```bash
challenges/v1/04-atlas-capstone/verify.sh --from-scratch
```

This command is destructive to work under `data_products/atlas_elt/datasets/`: it runs the
challenge reset first, applies the shipped solutions in learner order, exercises each documented
check, and restores the starter files on exit. Per-step commands and logs are retained under
`.devcontainer/verify/04-atlas-capstone/`, outside reset scope. Browser and Copilot Chat actions
are recorded separately in `interactions.tsv`; the runner validates their prompts and executable
acceptance checks, but does not claim to automate a human visual review or a nondeterministic chat
response. Use `--dry-run` to validate the phase and file manifests without resetting anything.

For a non-destructive plain-text synopsis of Phase 1 and all 14 Phase 2 challenges, including
each challenge's purpose, learner task, solution, and proof:

```bash
challenges/v1/04-atlas-capstone/verify.sh --review
```
