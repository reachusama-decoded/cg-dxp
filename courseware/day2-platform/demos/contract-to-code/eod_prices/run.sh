#!/usr/bin/env bash
# Build the contract-to-code example on DuckDB and show the price sheet.
set -euo pipefail
cd "$(dirname "$0")"
export EOD_DUCKDB_PATH="${EOD_DUCKDB_PATH:-$PWD/warehouse/eod_prices.duckdb}"
mkdir -p warehouse
dbt seed --full-refresh
dbt source freshness
dbt build
dbt show --select rpt_eod_prices_us --limit 12
