#!/usr/bin/env bash
# check-dag-load.sh — Airflow DAG-load check for the airflow-orchestration lab.
#
# Runs `airflow dags list-import-errors` plus structural probes (expected DAG
# IDs / task IDs in the DagBag) against the dags/ folder. This catches missing
# imports, decorator misuse, schedule-string parse errors, and DAG cycles —
# bugs that ast.parse / py_compile cannot see.
#
# The DAG imports `from include.alerting.notifications import send_alert` and
# `from callbacks import ...`, so both the lab root (for include.*) and the
# dags/ folder (for the sibling callbacks module) must be on PYTHONPATH.
#
# Databricks-only; no DuckDB.
# Preflight / client sign-off: missing Airflow or providers is SKIP, not PASS.
# Exit 2 on skip unless ALLOW_AIRFLOW_SKIP=1 (learner local convenience only).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DAGS_DIR="$SCRIPT_DIR/dags"
EXPECTED_DAGS="portfolio_analytics_daily portfolio_analytics_submit_run"
PRIMARY_DAG="portfolio_analytics_daily"
EXPECTED_TASKS="start source_freshness_check publish_to_catalog end"

# --- Locate an airflow CLI. ---
AIRFLOW_BIN=""
if command -v airflow >/dev/null 2>&1; then
  AIRFLOW_BIN="$(command -v airflow)"
fi
if [[ -z "$AIRFLOW_BIN" ]]; then
  echo "[skip] airflow CLI not on PATH — open the devcontainer (it ships Airflow 2.10)."
  if [[ "${ALLOW_AIRFLOW_SKIP:-0}" == "1" ]]; then
    echo "[note] ALLOW_AIRFLOW_SKIP=1 set — recording skip without failing (not a preflight PASS)."
    exit 0
  fi
  echo "[FAIL] Airflow not available; for client sign-off this is not a green gate. Set ALLOW_AIRFLOW_SKIP=1 only for local non-sign-off runs."
  exit 2
fi

AIRFLOW_PY="$(dirname "$AIRFLOW_BIN")/python"
[[ -x "$AIRFLOW_PY" ]] || AIRFLOW_PY="python3"

# Probe the providers / Cosmos the DAGs import.
if ! "$AIRFLOW_PY" -c "import cosmos; from airflow.providers.http.hooks.http import HttpHook; from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator" >/dev/null 2>&1; then
  echo "[skip] airflow found but cosmos / http / databricks providers not importable — rebuild the devcontainer."
  if [[ "${ALLOW_AIRFLOW_SKIP:-0}" == "1" ]]; then
    echo "[note] ALLOW_AIRFLOW_SKIP=1 set — recording skip without failing (not a preflight PASS)."
    exit 0
  fi
  echo "[FAIL] Airflow providers missing; for client sign-off this is not a green gate. Set ALLOW_AIRFLOW_SKIP=1 only for local non-sign-off runs."
  exit 2
fi

# --- Project-local AIRFLOW_HOME so we never touch ~/airflow. ---
export AIRFLOW_HOME="$SCRIPT_DIR/.airflow-verifier"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export AIRFLOW__CORE__DAGS_FOLDER="$DAGS_DIR"
mkdir -p "$AIRFLOW_HOME"

# Lab root (for include.alerting.*) + dags/ (for the sibling callbacks module).
export PYTHONPATH="$SCRIPT_DIR:$DAGS_DIR${PYTHONPATH:+:$PYTHONPATH}"

"$AIRFLOW_BIN" db migrate > "$AIRFLOW_HOME/db-init.log" 2>&1 || true

# --- The real test: list-import-errors. ---
LOG="$AIRFLOW_HOME/.list-import-errors.log"
"$AIRFLOW_BIN" dags list-import-errors > "$LOG" 2>&1

if grep -q "^No data found" "$LOG"; then
  err_count=0
else
  err_count=$(grep -cE "^/[^ ]+\.py" "$LOG" || true)
fi

if [[ "$err_count" -ne 0 ]]; then
  echo "[FAIL] airflow dags list-import-errors: $err_count import error(s)"
  cat "$LOG"
  exit 1
fi
echo "[pass] airflow dags list-import-errors: 0 errors (all DAGs load)"

# --- Structural probes via DagBag. ---
"$AIRFLOW_PY" - <<PY
import sys
from airflow.models import DagBag

root = "$SCRIPT_DIR"
dags_dir = "$DAGS_DIR"
for p in (root, dags_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

bag = DagBag(dag_folder=dags_dir)
if bag.import_errors:
    raise SystemExit(f"DagBag import errors: {bag.import_errors}")

expected_dags = "$EXPECTED_DAGS".split()
primary = "$PRIMARY_DAG"
expected_tasks = "$EXPECTED_TASKS".split()

missing = [did for did in expected_dags if did not in bag.dags]
if missing:
    raise SystemExit(f"Missing DAGs: {missing}")

dag = bag.dags[primary]
downstream = lambda tid: sorted(t.task_id for t in dag.get_task(tid).downstream_list)

if downstream("start") != ["source_freshness_check"]:
    raise SystemExit(f"Unexpected downstream for start: {downstream('start')}")
if not any(d.startswith("dbt_pipeline") for d in downstream("source_freshness_check")):
    raise SystemExit(f"dbt_pipeline missing after freshness check: {downstream('source_freshness_check')}")
if downstream("publish_to_catalog") != ["end"]:
    raise SystemExit(f"Unexpected downstream for publish_to_catalog: {downstream('publish_to_catalog')}")

for tid in expected_tasks:
    dag.get_task(tid)

print("Airflow DAG-load probe: PASS")
PY
exit 0
