# Atlas IDs, joins and report population — static review

Date: 5 October 2026. Purpose: investigate the owner's concern that missing IDs or joins may lose data, and define a useful Phase 1 learning objective. The machine-readable results and seed hashes are in [capstone-static-audit.json](capstone-static-audit.json). This is a read-only CSV/reference-SQL analysis, not a Databricks query result or a proof of the entire capstone runtime.

## Inputs and method

Read the seven CSVs under [Atlas seeds](../../data_products/atlas_elt/seeds) with Python's CSV reader. Check required primary/composite key columns, empty keys, duplicate keys and six raw foreign-key relationships. Inspect the reference SQL in [trade](../../challenges/04-atlas-capstone/solution/datasets/trades/dbt/integration/dom_trading__trade.sql), [position](../../challenges/04-atlas-capstone/solution/datasets/portfolios/dbt/integration/dom_positions__position.sql), [portfolio](../../challenges/04-atlas-capstone/solution/datasets/portfolios/dbt/integration/dom_portfolio__portfolio.sql), [latest price](../../challenges/04-atlas-capstone/solution/datasets/market_daily/dbt/integration/dom_trading__latest_price.sql) and [portfolio summary](../../challenges/04-atlas-capstone/solution/datasets/advisors/dbt/integration/rpt_portfolio_summary.sql).

For population analysis, apply the trade model's positive quantity/price and B/S filters, the dimensions' positive-ID filters, distinct portfolio/instrument grouping, instrument matching and portfolio/client/advisor matching. Latest prices derive from those same valid trades, so every represented instrument has a latest-price candidate. This reproduces key membership and row-population logic; it does **not** reproduce warehouse SQL type coercion, arithmetic precision, materialization, runtime timestamps, all models or all output totals. Compare with compiled SQL and live results in P3.

## Fixture integrity

| CSV | Rows | Key | Missing key columns / empty keys / duplicate key groups |
|---|---:|---|---|
| trades | 10,000 | trade_id | 0 / 0 / 0 |
| instruments | 1,502 | instrument_id | 0 / 0 / 0 |
| portfolios | 2,501 | portfolio_id | 0 / 0 / 0 |
| clients | 2,002 | client_id | 0 / 0 / 0 |
| advisors | 120 | advisor_id | 0 / 0 / 0 |
| funds | 60 | fund_id | 0 / 0 / 0 |
| fund_holdings | 3,205 | fund_id + instrument_id | 0 / 0 / 0 |

The raw relationships checked are trades→portfolios, trades→instruments, portfolios→clients, portfolios→advisors, fund_holdings→funds and fund_holdings→instruments. Each has zero orphan rows in these supplied fixtures. Presence of a key is not the same as its business validity: the dimensions deliberately filter non-positive IDs, leaving 1,500 instruments, 2,500 portfolios, 2,000 clients and 120 advisors.

The expected reference transformations retain `portfolio_id` and `instrument_id` at position grain and retain `portfolio_id`, `client_id` and `advisor_id` in the portfolio summary. Aggregated advisor/region outputs have different grains; the absence of portfolio ID there is not automatically data loss. Learner-authored models can still omit a key, fan out a join or use a wrong grain; those cases need actual task checks.

## Population result

| Step | Static result | Interpretation |
|---|---:|---|
| Raw trades | 10,000 | Original fixture. |
| Invalid trades removed by declared filters | 120 | Expected quality filtering; explain why these are excluded. |
| Valid trades | 9,880 | Starting fact population for positions/latest price. |
| Distinct valid portfolio/instrument groups | 3,717 | Position grain, not trade grain. |
| Positions after instrument/latest-price membership | 3,717 | No checked group is lost here. |
| Positions lost at portfolio/client/advisor joins | 0 | No checked position is lost here. |
| Valid portfolio dimension | 2,500 | Broader population than trade-driven output. |
| Distinct portfolio IDs in summary | 1,028 | Portfolios having qualifying trades. |
| Valid portfolios absent from summary | 1,472 | Have no qualifying trades in this fixture. |

The current `rpt_portfolio_summary` starts from positions, then inner-joins portfolio and party dimensions. It therefore cannot include portfolios that never entered the valid trade/position population. This explains a substantial population difference without a missing ID column or an orphaned trade key. It does not establish whether that difference is acceptable for the consumer.

## What is already clear, and what needs improvement

The current guide explains intentional invalid-trade filters. Phase 2 relationship-test challenge 8 explicitly warns that an orphan trade portfolio can disappear through an inner join. That useful explanation is currently advanced/optional, while Phase 1's not-null portfolio test is an optional variation. Neither is a full consumer-population contract. Also, reconciling three reports all derived from the same incomplete driving relation can pass while every report omits the same portfolios.

The guide should name the expected output population: “portfolios with qualifying trades in this fixture” or “all valid portfolios, including zero activity.” The latter requires an explicit redesign from the portfolio dimension with left joins and chosen null/zero semantics. Do not claim a portfolio has zero assets merely because the fixture has no trades for it; zero observed activity and economic zero holdings are different statements.

## Proposed learner investigation

1. State the raw trade grain, position grain and consumer report grain; identify keys to retain.
2. Count raw and valid trades and explain the 120 removed rows using the declared business rules.
3. Count valid portfolios and reported portfolios; anti-join to identify the absent population.
4. Verify trade→portfolio and trade→instrument relationships and parent uniqueness; explain why not-null alone cannot prove a join safe.
5. Decide the expected consumer population from a supplied requirement, not from whichever query happened to run.
6. Use a small deliberate fixture defect to show that an unmatched key is caught; repair it and inspect population/output again.
7. Demonstrate an independent population check alongside financial reconciliation, with a short explanation of any expected exclusions.

Place the minimum subset in Phase 1. Keep complex null/zero handling, generalized tests or broader source remediation as optional advanced work when appropriate. A defective fixture must be explicitly declared in starter Check text; it must not corrupt the canonical CSVs used by other challenges.

## Outstanding implementation review

Run exact model counts and anti-joins in the prepared warehouse using the actual seed/profile types. Check output column schemas, key uniqueness at every join, retained trade counts/fees and expected totals against an independently authored oracle. Review tie-breaking, currency limitations and any separate fund-holding joins as additional concerns; this static membership review does not certify them. Confirm the consumer population decision before adjusting source data, joins or certification checks.

No dataset or model has been changed to “fix” these findings in the planning delivery.
