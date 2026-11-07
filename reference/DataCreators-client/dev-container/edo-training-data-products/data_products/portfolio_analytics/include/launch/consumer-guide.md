# Client Portfolio Analytics — Consumer Guide

This is an illustrative consumer guide for the native platform product, not a live-service promise. Assigned v2 work publishes classroom output evidence; its entry is [Portfolio Analytics](../../../../challenges/v2/dbt/README.md). Namespace values and queries below belong to this reference scenario, not the prefixed v2 attempt.

## What is this data product?

Client Portfolio Analytics publishes a daily, base-currency view of every fund's
holdings and exposure. The portfolio-analytics dbt pipeline reads custodian
holdings, Bloomberg prices, FX rates, and the fund master, and produces three
consumer-facing marts on Databricks. Its target promise is a weekday refresh by **07:30 UK** for the prior business-day close.

## Where do I find it?

| Field | Value |
|-------|-------|
| Databricks catalog | `training_dev` (training) / the team's prod catalog |
| Schema | `training_<username>` (training) / `portfolio_analytics` (prod) |
| Marts | `fct_portfolio_returns`, `agg_fund_exposure`, `agg_fund_daily_exposure` |

## The three marts

| Mart | Grain | Use it for |
|------|-------|-----------|
| `fct_portfolio_returns` | one row per (fund, date, instrument) | position-level GBP market value and the holdings value per synthetic unit |
| `agg_fund_exposure` | one row per (fund, date, strategy) | total and cash exposure by strategy, plus instrument count — compliance concentration |
| `agg_fund_daily_exposure` | one row per (fund, date) | whole-fund exposure across all strategies — the headline daily number |

## Sample queries

> All three marts materialise into the single pre-provisioned training schema, `training_dev.training_<username>` — the training catalog gives each person exactly one schema and the dbt project separates its layers by tag rather than by schema. Substitute your own schema (it is the `DBT_SCHEMA` value in your shell) for `training_<username>` below.

> These read the **latest loaded** `position_date` rather than `current_date()`. The training
> fixtures carry fixed historical dates (2026-05-20/21), so `current_date()` matches nothing and the
> queries come back empty; a real feed would use its declared reporting date, which need not equal the execution date.

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

### A fund's positions and holdings value per synthetic unit

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
| `calc_nav_per_unit` | fct | compatibility name for holdings-only GBP exposure / 100 million synthetic units; not official NAV |
| `strategy_code` | agg | strategy (`EQ-LC`, `EQ-EM`, `EQ-GC`, `FI-IG`) |
| `exposure_base_ccy` | agg | total base-ccy exposure for the (fund, date, strategy) |
| `cash_exposure_base_ccy` | agg | the cash slice of that exposure |
| `total_exposure_base_ccy` | agg_daily | whole-fund exposure for the (fund, date), summed across strategies |
| `total_cash_base_ccy` | agg_daily | the cash slice of that whole-fund exposure |

## Known limitations

- **Holdings value per synthetic unit** retains the compatibility identifier `calc_nav_per_unit`. The current teaching measure divides holdings-only GBP exposure by 100 million synthetic units and excludes cash. It does not include complete net assets/liabilities, actual outstanding fund shares or share-class accounting, and it is not official NAV or a custodian-published share price. A historical test named `assert_nav_within_tolerance` is a fixture comparison; it cannot establish official custodian NAV reconciliation.
- **Inactive funds** are filtered out at the intermediate layer (`is_active = true`); a wound-down fund will not appear.
- **End-of-day only** — the marts reflect close positions, not intraday.

## Data freshness

- Target SLA: published by **07:30 UK** on weekdays.
- Sources land overnight: custodian by 02:00 UK, Bloomberg + FX by 03:00 UK.
- The production design requires a configured Datadog alert and a Teams incident notice when delivery is delayed; verify those integrations before relying on them.

## Contact

| Channel | Purpose |
|---------|---------|
| Microsoft Teams `portfolio-analytics` | questions, feature requests |
| Datadog + Microsoft Teams | automatic alerts (Datadog) and incident notices (Teams) |
| xMatters `portfolio-analytics-oncall` | production incidents out of hours (paged from Datadog) |
