# dbt independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare dbt phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| dbt-p1-01 | `evidence.md` |
| dbt-p1-02 | `models/sources.yml`, `models/staging/stg_holdings.sql`, `evidence.md` |
| dbt-p1-03 | `models/staging/stg_holdings.sql`, `tests/holdings_grain.sql`, `evidence.md` |
| dbt-p1-04 | `models/marts/fund_nav_report.sql`, `evidence.md` |
| dbt-p1-05 | `models/schema.yml`, `tests/holdings_grain.sql`, `tests/matched_funds.sql`, `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`, `evidence.md` |

## Declared baseline

These focus files are intentionally unfinished: `models/staging/stg_holdings.sql`, `models/marts/fund_nav_report.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.
