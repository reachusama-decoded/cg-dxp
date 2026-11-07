# dbt independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare dbt phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| dbt-p2-01 | `models/intermediate/int_holdings_enriched.sql`, `evidence.md` |
| dbt-p2-02 | `models/intermediate/int_holdings_enriched.sql`, `macros/native_value.sql`, `evidence.md` |
| dbt-p2-03 | `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`, `models/schema.yml`, `evidence.md` |
| dbt-p2-04 | `models/marts/holdings_replay.sql`, `evidence.md` |
| dbt-p2-05 | `models/marts/fund_nav_report.sql`, `snapshots/fund_history.sql`, `models/schema.yml`, `evidence.md` |

## Declared baseline

These focus files are intentionally unfinished: `macros/native_value.sql`, `models/marts/holdings_replay.sql`, `snapshots/fund_history.sql`, `models/marts/fund_nav_report.sql`, `models/intermediate/int_holdings_enriched.sql`, `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.
