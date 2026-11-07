# Portfolio Analytics on DuckDB (instructor copy of challenge 02)

The learners' `challenges/v1/02-dbt-pipeline` solution with the same model names, layers, tags, seeds and tests, and DuckDB in place of Databricks. Two adaptations: the Databricks `OPTIMIZE ... ZORDER` post-hook is a macro that does nothing on DuckDB (`macros/optimize_mart.sql`), and one decimal cast in `int_holdings_enriched` is widened because DuckDB's decimal arithmetic is stricter. A `stretch` folder adds what a production project has on top: a dispatching macro, a reusable macro, a custom generic test, a snapshot, an incremental model, a unit test and an exposure.

| README section (learners) | Here |
|---|---|
| S1 inspect the raw data | `dbt seed`, then query the seeds |
| S2 read the project | `dbt ls --resource-type model`; `dbt_project.yml` |
| S3 sources and freshness | `models/sources.yml`; `dbt source freshness` |
| S4 `stg_holdings` | `models/staging/stg_holdings.sql` |
| S5 to S7 the staging layer | `dbt build --select tag:staging` |
| S8 a staging test | `models/staging/schema.yml`; `dbt test --select stg_holdings` |
| C1 to C4 intermediate and marts | `models/intermediate/`, `models/marts/` |
| C5 and C6 tests | `models/marts/schema.yml`, `tests/assert_nav_within_tolerance.sql` |
| C7 full build | `dbt build --exclude tag:stretch` |
| C8 docs | `dbt docs generate`; `dbt docs serve --host 127.0.0.1 --port 8081` |
| C9 post-hook | `macros/optimize_mart.sql` |
| C10 capstone mart | `models/marts/agg_fund_daily_exposure.sql`, `tests/reconcile_daily_exposure.sql` |
| Stretch | `models/stretch/`, `snapshots/`, `tests/generic/`, `macros/to_base_ccy.sql`, `models/exposures.yml` |

`bash demo.sh` runs the whole sequence and `bash demo.sh stretch` adds the stretch pieces. The warehouse file is `warehouse/training_dev.duckdb` (schema `training_demo`); the script regenerates it.
