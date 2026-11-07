# Service levels for the US end-of-day price sheet

Vocabulary used on Day 2: an **SLI** is the thing you measure; the **SLO** is its ideal value; the **SLA** is the permissible departure from that ideal, agreed with the consumer, and what happens when it is breached.

| Promise | SLI (what is measured) | SLO (ideal) | SLA (agreed tolerance and response) | Measured how |
|---|---|---|---|---|
| Delivery | Minutes after 07:30 America/New_York at which `rpt_eod_prices_us` for the business date is published | 0 | Published by 07:30 ET on US business days; a run expected to miss is announced by 07:00 ET; later than 07:45 ET is a breach, logged and explained the same day | Airflow DAG end time vs 07:30 ET, per run |
| Completeness | Share of active US instruments with a price for the business date | 100% | ≥ 99.5% per day; below that the sheet is still published with the missing instruments listed | `assert_us_completeness` singular test, per run |
| Freshness of inputs | Hours between the vendor file's receipt and the run; same for the FX file | Vendor by 21:30 ET the previous evening, FX by 17:30 ET | Warn after 12 h, fail the run after 24 h; a failed freshness gate blocks publication rather than publishing stale rates | `dbt source freshness` thresholds in `sources.yml`; the DAG's first task |
| Accuracy | Count of prices that moved more than 5% day on day without an explanation attached | 0 | A flagged move is explained to the consumer within 2 business hours of the sheet | Day-on-day comparison in a monitoring query; duty to explain tracked per instrument |
| Availability | Share of business-hour minutes the table answers a query in Databricks | 100% | ≥ 99.5% per month | Platform monitoring of the warehouse |
| Support | Hours to a first response to a consumer query during 06:00–18:00 ET | 1 | ≤ 2 business hours | Team channel response time |

## What is not promised

- Real-time or intraday prices. The product is a daily close.
- Valuation. The sheet gives a price in USD and the rate used; what a holding is worth is a different product.
- Prices for inactive or non-US instruments. They exist in the intermediate layer and can be filtered into a sibling product.

## Nines, for calibration

| Availability | Downtime a year | A way to remember it |
|---|---|---|
| 90% | about 36 days | a month |
| 99% | about 3.65 days | a working week |
| 99.9% | about 8.8 hours | a working day |
| 99.99% | about 53 minutes | an hour |
| 99.999% | about 5 minutes | a coffee |

Each extra nine costs about ten times more: cloned infrastructure, load balancing, a disaster-recovery site that already takes a slice of live traffic. The number of nines a provider offers tells you how much spare capacity it keeps.
