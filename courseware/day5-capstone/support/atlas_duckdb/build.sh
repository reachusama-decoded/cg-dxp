#!/usr/bin/env bash
# Build the whole Atlas solution on DuckDB, layer by layer as the capstone guide does.
set -euo pipefail
cd "$(dirname "$0")"
export ATLAS_DUCKDB_PATH="${ATLAS_DUCKDB_PATH:-$PWD/warehouse/training_dev.duckdb}"
export ATLAS_SCHEMA="${ATLAS_SCHEMA:-training_demo}"
mkdir -p warehouse
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
step "debug"                         ; dbt debug
step "seed the seven Atlas extracts" ; dbt seed --full-refresh
step "source-aligned layer"          ; dbt run --select tag:source-aligned
step "domain-aligned layer"          ; dbt run --select tag:domain-aligned
step "consumer-aligned layer"        ; dbt run --select tag:consumer-aligned
step "all tests"                     ; dbt test
step "snapshot (Phase 2, C11)"       ; dbt snapshot
step "incremental twin, second run (Phase 2, C10)"; dbt run --select ts_daily_market_incremental
step "docs"                          ; dbt docs generate
step "done"
