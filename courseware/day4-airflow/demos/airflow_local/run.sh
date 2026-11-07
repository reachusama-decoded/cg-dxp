#!/usr/bin/env bash
# Day 4 Airflow demo helper. Learners type the same astro commands in their container.
#   bash run.sh start              build the image and start Airflow (first time: several minutes)
#   bash run.sh seed               load both dbt projects' seeds into the container's DuckDB files
#   bash run.sh trigger [dag_id]   unpause + trigger (default portfolio_analytics_daily)
#   bash run.sh wait    [dag_id]   poll until the latest run finishes
#   bash run.sh status  [dag_id]   latest runs and the task states of the newest one
#   bash run.sh stale              make the custodian feed look two days old (freshness gate fails)
#   bash run.sh fresh              stamp the feed as just received again
#   bash run.sh logs | stop | kill | ui
set -euo pipefail
cd "$(dirname "$0")"
DAG="${2:-portfolio_analytics_daily}"
DBT=/home/astro/.venv/cosmos/bin/dbt
PY=/home/astro/.venv/cosmos/bin/python
WH=/usr/local/airflow/include/warehouse/training_dev.duckdb
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
    inpod "cd /usr/local/airflow/dags/eod_prices/dbt && $DBT seed --full-refresh --profiles-dir . --target local" | quiet ;;
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
  stale)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('$WH'); c.execute(\\\"update training_demo.holdings_raw set _extracted_at = now() - interval 2 day\\\"); print('custodian feed now looks 2 days old')\"" ;;
  fresh)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('$WH'); c.execute(\\\"update training_demo.holdings_raw set _extracted_at = now()\\\"); print('custodian feed stamped as fresh')\"" ;;
  *) sed -n '2,11p' "$0" ;;
esac
