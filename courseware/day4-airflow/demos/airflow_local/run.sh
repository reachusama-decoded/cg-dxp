#!/usr/bin/env bash
# Day 4 Airflow demo helper. Learners type the same astro commands in their container.
#   bash run.sh start              build the image and start Airflow (first time: several minutes)
#   bash run.sh seed               load every product's seeds into the container's DuckDB files
#   bash run.sh trigger [dag_id]   unpause + trigger (default portfolio_analytics_daily)
#   bash run.sh wait    [dag_id]   poll until the latest run finishes
#   bash run.sh status  [dag_id]   latest runs and the task states of the newest one
#   bash run.sh stale   [dag_id]   make the DAG's gated feed look two days old (the freshness gate fails)
#   bash run.sh fresh   [dag_id]   stamp the feed as just received again
#   bash run.sh dbt <product> ...  run a dbt command inside the scheduler, in dags/<product>/dbt
#   bash run.sh unwire | wire      price_sheet_daily: put the TODO back, or replace it with the dependency chain
#   bash run.sh alerts  [dag_id]   what the alert callbacks logged in the latest failed run: ticket (P3), Datadog (P1), Teams (P2)
#   bash run.sh logs | stop | kill | ui
set -euo pipefail
cd "$(dirname "$0")"
DAG="${2:-portfolio_analytics_daily}"
DBT=/home/astro/.venv/cosmos/bin/dbt
PY=/home/astro/.venv/cosmos/bin/python
WH=/usr/local/airflow/include/warehouse/training_dev.duckdb
# The feed each DAG's freshness gate watches: warehouse file, table, timestamp column, name.
case "$DAG" in
  price_sheet_daily) FEED_WH=/usr/local/airflow/include/warehouse/price_sheet.duckdb; FEED_TABLE=demo.vendor_prices_raw; FEED_COL=vendor_ts; FEED_NAME="vendor price feed" ;;
  *)                 FEED_WH=$WH; FEED_TABLE=training_demo.holdings_raw; FEED_COL=_extracted_at; FEED_NAME="custodian feed" ;;
esac
PS_DAG="dags/price_sheet/dags/price_sheet_daily.py"
PS_TODO="    # TODO: wire start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end"
PS_CHAIN="    start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end"
quiet() { grep -vE 'Astro managed secrets backend|^Running: airflow' || true; }
sched() { docker ps --format '{{.Names}}' | grep -- '-scheduler-1' | head -1; }
inpod() { local c; c="$(sched)"; [[ -n "$c" ]] || { echo "scheduler container not running: bash run.sh start" >&2; exit 1; }; docker exec -i "$c" bash -lc "$*"; }
runs_json() { astro dev run dags list-runs "$DAG" --output json 2>/dev/null | sed -n '/^\[/,$p'; }
latest() { runs_json | python3 -c "import sys,json; r=json.load(sys.stdin); r.sort(key=lambda x: x.get('run_after') or '', reverse=True); print((r[0]['$1'] if r else '') if r else '')" 2>/dev/null; }
case "${1:-}" in
  start)   astro dev start --wait 8m ;;
  stop)    astro dev stop ;;
  kill)    astro dev kill ;;
  logs)    astro dev logs -f ;;
  ui)      open "http://localhost:8080" ;;
  seed)
    inpod "cd /usr/local/airflow/dags/portfolio_analytics/dbt && $DBT seed --full-refresh --profiles-dir . --target local" | quiet
    inpod "cd /usr/local/airflow/dags/eod_prices/dbt && $DBT seed --full-refresh --profiles-dir . --target local" | quiet
    inpod "cd /usr/local/airflow/dags/price_sheet/dbt && $DBT seed --full-refresh --profiles-dir . --target local" | quiet ;;
  dbt)
    PRODUCT="${2:?usage: bash run.sh dbt <product> <dbt arguments>}"; shift 2
    inpod "cd /usr/local/airflow/dags/$PRODUCT/dbt && $DBT $(printf '%q ' "$@") --profiles-dir . --target local" | quiet ;;
  unwire)
    PS_DAG="$PS_DAG" OLD="$PS_CHAIN" NEW="$PS_TODO" python3 -c "import os,pathlib; p=pathlib.Path(os.environ['PS_DAG']); p.write_text(p.read_text().replace(os.environ['OLD'], os.environ['NEW']))"
    grep -n "TODO: wire" "$PS_DAG" ;;
  wire)
    PS_DAG="$PS_DAG" OLD="$PS_TODO" NEW="$PS_CHAIN" python3 -c "import os,pathlib; p=pathlib.Path(os.environ['PS_DAG']); p.write_text(p.read_text().replace(os.environ['OLD'], os.environ['NEW']))"
    grep -n ">>" "$PS_DAG" ;;
  trigger)
    astro dev run dags unpause "$DAG" 2>/dev/null | quiet >/dev/null || true
    astro dev run dags trigger "$DAG" 2>/dev/null | quiet | tail -3 ;;
  wait)
    for i in $(seq 1 60); do
      S="$(latest state)"; echo "t+$((i*10))s $DAG state=${S:-unknown}"
      [[ "$S" == "success" || "$S" == "failed" ]] && break; sleep 10
    done ;;
  status)
    astro dev run dags list-runs "$DAG" 2>/dev/null | quiet | head -8
    RUN_ID="$(latest run_id)"
    [[ -n "$RUN_ID" ]] && astro dev run tasks states-for-dag-run "$DAG" "$RUN_ID" 2>/dev/null | quiet ;;
  alerts)
    inpod "cd /usr/local/airflow/logs/dag_id=$DAG && R=\$(grep -l 'datadog stub' run_id=*/task_id=*/attempt=*.log 2>/dev/null | xargs ls -t 2>/dev/null | head -1 | cut -d/ -f1) && [ -n \"\$R\" ] && echo \"\$R\" && cat \$R/task_id=*/attempt=*.log | grep -o 'ticket stub. summary=[^\"]*)\\|datadog stub. severity=[^\"]*oncall\\|send_alert skipped[^|]*' | sed 's/^/  /' || echo 'no failed run with alert lines yet'" ;;
  stale)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('$FEED_WH'); c.execute(\\\"update $FEED_TABLE set $FEED_COL = now() - interval 2 day\\\"); print('$FEED_NAME now looks 2 days old')\"" ;;
  fresh)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('$FEED_WH'); c.execute(\\\"update $FEED_TABLE set $FEED_COL = now()\\\"); print('$FEED_NAME stamped as fresh')\"" ;;
  *) sed -n '2,14p' "$0" ;;
esac
