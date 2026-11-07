#!/usr/bin/env bash
# End-to-end run of the Day 3 dbt demo on DuckDB. Mirrors the challenge's section order.
# Usage: bash demo.sh            (full run)      bash demo.sh stretch   (adds the stretch pieces)
set -euo pipefail
cd "$(dirname "$0")"
export PA_DUCKDB_PATH="${PA_DUCKDB_PATH:-$PWD/warehouse/training_dev.duckdb}"
export PA_SCHEMA="${PA_SCHEMA:-training_demo}"
mkdir -p warehouse
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }

step "S0  dbt debug: profile, connection, project"           ; dbt debug
step "S1  seed the six raw feeds and two reference seeds"     ; dbt seed --full-refresh
step "S2  list the models before building anything"          ; dbt ls --resource-type model --exclude tag:stretch
step "S3  source freshness (5 of 6 tables carry a load field)"; dbt source freshness
step "S4  build one model and look at it"                    ; dbt build --select stg_holdings; dbt show --select stg_holdings --limit 5
step "S5-S7 build the whole staging layer by tag"            ; dbt build --select tag:staging
step "S8  a staging test is just a query that must return no rows"; dbt test --select stg_holdings
step "C1-C7 full build: intermediate, marts, generic + singular tests"; dbt build --exclude tag:stretch
step "C8  docs and lineage (open target/index.html)"         ; dbt docs generate
step "C10 the capstone mart and its reconciliation"          ; dbt show --select agg_fund_daily_exposure --limit 10
if [[ "${1:-}" == "stretch" ]]; then
  step "X1  snapshot the fund master (SCD2)"                 ; dbt snapshot
  step "X2  incremental mart, run twice"                     ; dbt run --select agg_fund_daily_exposure_incremental; dbt run --select agg_fund_daily_exposure_incremental
  step "X3  custom generic test + unit test"                 ; dbt test --select agg_fund_daily_exposure_incremental stg_holdings,test_type:unit
fi
step "done"
