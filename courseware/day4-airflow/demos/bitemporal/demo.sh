#!/usr/bin/env bash
# Three loads: day 1 full file, day 2 full file (a tenure change and a job-title defect),
# then a corrected re-delivery of day 2. Shows as-is, as-of and as-was afterwards.
set -euo pipefail
cd "$(dirname "$0")"
export BT_DUCKDB_PATH="${BT_DUCKDB_PATH:-$PWD/warehouse/bitemporal.duckdb}"
mkdir -p warehouse; rm -f "$BT_DUCKDB_PATH"
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
step "seed the feed (three batches in one CSV)";           dbt seed --full-refresh
step "load 1: business date 2026-11-02, full file";       dbt run --vars '{batch: D1}'
sleep 1
step "load 2: business date 2026-11-03 (tenure +1 for 1001; title lost its 'II'; new joiner 1004)"; dbt run --vars '{batch: D2}'
sleep 1
T_BEFORE_CORRECTION="$(date -u +'%Y-%m-%d %H:%M:%S')"
sleep 1
step "load 3: corrected re-delivery for 2026-11-03 (title restored)"; dbt run --vars '{batch: D2-CORR}'
step "query it"; python show.py "$T_BEFORE_CORRECTION"
