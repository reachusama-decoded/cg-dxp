#!/usr/bin/env bash
#
# verify-with-databricks.sh — the verification gate for the airflow-orchestration
# lab.
#
# Two parts, both Databricks-only (no DuckDB):
#   1. The DAGs load: `astro dev parse` if the Astro CLI is present, plus the
#      DagBag check in check-dag-load.sh (catches import / decorator / schedule
#      / cycle errors that ast.parse cannot see).
#   2. The orchestrated dbt project builds on Databricks: `dbt debug` then a
#      full `dbt build` against the databricks profile — the same models the
#      DAG runs, proving the pipeline the orchestrator drives is green.
#
# Auth is OAuth via `databricks auth login` (run by
# .devcontainer/setup-databricks-dbt.sh); `.mise/env.sh` mints a short-lived
# DBT_ACCESS_TOKEN from that OAuth session, so the dbt profile authenticates with
# that token and there is no static token to set.
#
# Required environment for part 2:
#   DATABRICKS_HOST        e.g. adb-1234.5.azuredatabricks.net
#   DATABRICKS_HTTP_PATH   e.g. /sql/1.0/warehouses/<warehouse-id>
# Optional:
#   DBT_CATALOG, DBT_SCHEMA    defaults: catalog training_dev, schema training_<username>.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() {
  echo
  echo "=================================================="
  echo "  Databricks verification: FAIL"
  echo "  $1"
  echo "=================================================="
  exit 1
}

# --- Part 1: DAGs load -------------------------------------------------------
echo "== DAG load check =="

if command -v astro >/dev/null 2>&1; then
  echo "-- astro dev parse --"
  ( cd "$ROOT" && astro dev parse ) || fail "astro dev parse reported DAG import errors."
else
  echo "  astro CLI not found — relying on check-dag-load.sh for the DagBag check."
fi

echo "-- check-dag-load.sh --"
# Do not export ALLOW_AIRFLOW_SKIP for client sign-off; skip is not a pass.
bash "$ROOT/check-dag-load.sh" || fail "check-dag-load.sh reported DAG-load errors or skipped (Airflow missing)."

# --- Part 2: orchestrated dbt project builds on Databricks -------------------
if [ -z "${DATABRICKS_HOST:-}" ] || [ -z "${DATABRICKS_HTTP_PATH:-}" ]; then
  echo
  echo "DATABRICKS_HOST and DATABRICKS_HTTP_PATH are not set." >&2
  echo "Run bash .devcontainer/setup-databricks-dbt.sh, or export them, then re-run." >&2
  fail "Databricks connection env vars are not set (part 2 cannot run)."
fi

echo
echo "Databricks build of the orchestrated dbt project"
echo "  host:         $DATABRICKS_HOST"
echo "  http_path:    $DATABRICKS_HTTP_PATH"
echo "  catalog:      ${DBT_CATALOG:-<profile default: training_dev>}"
echo "  schema:       ${DBT_SCHEMA:-<profile default: training_${USER:-student}>}"
echo

cd "$ROOT/dbt"

echo "== dbt debug =="
dbt debug || fail "dbt debug could not connect to Databricks."

echo
echo "== dbt build (seeds + 10 models + all tests) =="
dbt build
build_status=$?
if [ "$build_status" -ne 0 ]; then
  fail "dbt build reported seed, model or test failures (exit $build_status)."
fi

echo
echo "=================================================="
echo "  Databricks verification: PASS"
echo "  DAGs loaded (not skipped) and the orchestrated dbt build is green on Databricks."
echo "=================================================="
