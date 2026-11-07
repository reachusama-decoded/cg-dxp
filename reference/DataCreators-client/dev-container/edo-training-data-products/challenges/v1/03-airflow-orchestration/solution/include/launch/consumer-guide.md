# Client Portfolio Analytics — Consumer Guide

## What is this data product?

Client Portfolio Analytics publishes a daily, base-currency view of every fund's
holdings and exposure. The portfolio-analytics dbt pipeline reads custodian
holdings, Bloomberg prices, FX rates, and the fund master, and produces two
consumer-facing marts on Databricks. The data refreshes every weekday by **07:30
UK**, reflecting positions as of the prior business-day close.

## Where do I find it?

| Field | Value |
|-------|-------|
| Databricks catalog | `training_dev` (training) / the team's prod catalog |
| Schema | `training_<username>` (training) / `portfolio_analytics` (prod) |
| Marts | `fct_portfolio_returns`, `agg_fund_exposure`, `agg_fund_daily_exposure` |

## The three marts

| Mart | Grain | Use it for |
|------|-------|-----------|
| `fct_portfolio_returns` | one row per (fund, date, instrument) | position-level base-ccy market value and the fund's calculated NAV-per-unit |
| `agg_fund_exposure` | one row per (fund, date, strategy) | total and cash exposure by strategy, plus instrument count — compliance concentration |
| `agg_fund_daily_exposure` | one row per (fund, date) | whole-fund exposure across all strategies — the headline daily number |

## Sample queries

> All three marts materialise into the single pre-provisioned training schema, `training_dev.training_<username>` — the training catalog gives each person exactly one schema and the dbt project separates its layers by tag rather than by schema. Substitute your own schema (it is the `DBT_SCHEMA` value in your shell) for `training_<username>` below.

> These read the **latest loaded** `position_date` rather than `current_date()`. The training
> fixtures carry fixed historical dates (2026-05-20/21), so `current_date()` matches nothing and the
> queries come back empty; a real daily feed would land today's date and both forms would agree.

### Latest exposure by fund and strategy

```sql
SELECT
    fund_id,
    strategy_code,
    exposure_base_ccy,
    cash_exposure_base_ccy,
    instrument_count
FROM training_dev.training_<username>.agg_fund_exposure
WHERE position_date = (SELECT max(position_date) FROM training_dev.training_<username>.agg_fund_exposure)
ORDER BY exposure_base_ccy DESC
```

### A fund's positions and NAV-per-unit

```sql
SELECT
    instrument_id,
    quantity,
    mv_base_ccy,
    calc_nav_per_unit
FROM training_dev.training_<username>.fct_portfolio_returns
WHERE fund_id = 'PEF-LARGE-CAP'
  AND position_date = (SELECT max(position_date) FROM training_dev.training_<username>.fct_portfolio_returns)
ORDER BY mv_base_ccy DESC
```

### Whole-fund daily exposure

```sql
SELECT
    fund_id,
    total_exposure_base_ccy,
    total_cash_base_ccy
FROM training_dev.training_<username>.agg_fund_daily_exposure
WHERE position_date = (SELECT max(position_date) FROM training_dev.training_<username>.agg_fund_daily_exposure)
ORDER BY total_exposure_base_ccy DESC
```

## Key columns

| Column | Mart | Description |
|--------|------|-------------|
| `fund_id` | all | fund identifier |
| `position_date` | all | as-of business date |
| `instrument_id` | fct | ISIN, or a `CASH_<ccy>` id for cash holdings |
| `mv_base_ccy` | fct | market value converted to the GBP base currency |
| `calc_nav_per_unit` | fct | calculated NAV-per-unit (reconciled to the custodian NAV within 1bp) |
| `strategy_code` | agg | strategy (`EQ-LC`, `EQ-EM`, `EQ-GC`, `FI-IG`) |
| `exposure_base_ccy` | agg | total base-ccy exposure for the (fund, date, strategy) |
| `cash_exposure_base_ccy` | agg | the cash slice of that exposure |
| `total_exposure_base_ccy` | agg_daily | whole-fund exposure for the (fund, date), summed across strategies |
| `total_cash_base_ccy` | agg_daily | the cash slice of that whole-fund exposure |

## Known limitations

- **NAV-per-unit** is calculated against a synthesised units-outstanding figure; it reconciles to the custodian-reported NAV within 1 basis point (enforced by a dbt test), but it is not the custodian's published NAV.
- **Inactive funds** are filtered out at the intermediate layer (`is_active = true`); a wound-down fund will not appear.
- **End-of-day only** — the marts reflect close positions, not intraday.

## Data freshness

- Target SLA: published by **07:30 UK** on weekdays.
- Sources land overnight: custodian by 02:00 UK, Bloomberg + FX by 03:00 UK.
- If the run is delayed, an automatic Datadog alert fires and a notification is posted to the Microsoft Teams channel.

## Contact

| Channel | Purpose |
|---------|---------|
| Microsoft Teams `portfolio-analytics` | questions, feature requests |
| Datadog + Microsoft Teams | automatic alerts (Datadog) and incident notices (Teams) |
| xMatters `portfolio-analytics-oncall` | production incidents out of hours (paged from Datadog) |
