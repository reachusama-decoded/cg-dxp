#!/usr/bin/env bash
# Day 4 Airflow demo helper. Learners type the same astro commands in their container.
#   bash run.sh start     build the image and start Airflow (first time: several minutes)
#   bash run.sh seed      load both dbt projects' seeds into the container's DuckDB files
#   bash run.sh trigger [dag_id]   unpause + trigger (default portfolio_analytics_daily)
#   bash run.sh status  [dag_id]   runs and task states
#   bash run.sh stale     make the custodian feed look two days old (freshness gate fails)
#   bash run.sh fresh     stamp the feed as just received again
#   bash run.sh logs | stop | kill | ui
set -euo pipefail
cd "$(dirname "$0")"
DAG="${2:-portfolio_analytics_daily}"
DBT=/home/astro/.venv/cosmos/bin/dbt
PY=/home/astro/.venv/cosmos/bin/python
sched() { docker ps --format '{{.Names}}' | grep -- '-scheduler-1' | head -1; }
inpod() { local c; c="$(sched)"; [[ -n "$c" ]] || { echo "scheduler container not running: bash run.sh start" >&2; exit 1; }; docker exec -i "$c" bash -lc "$*"; }
case "${1:-}" in
  start)   astro dev start --wait 5m ;;
  stop)    astro dev stop ;;
  kill)    astro dev kill ;;
  logs)    astro dev logs -f ;;
  ui)      open "http://localhost:8080" ;;
  seed)
    inpod "cd /usr/local/airflow/dags/portfolio_analytics/dbt && $DBT seed --full-refresh --profiles-dir . --target local"
    inpod "cd /usr/local/airflow/dags/eod_prices/dbt && $DBT seed --full-refresh --profiles-dir . --target local" ;;
  trigger)
    astro dev run dags unpause "$DAG" >/dev/null || true
    astro dev run dags trigger "$DAG" ;;
  status)
    astro dev run dags list-runs "$DAG" 2>/dev/null | head -8
    RUN_ID=$(astro dev run dags list-runs "$DAG" --output json 2>/dev/null | python3 -c "import sys,json; r=json.load(sys.stdin); print(r[0]['run_id'] if r else '')")
    [[ -n "$RUN_ID" ]] && astro dev run tasks states-for-dag-run "$DAG" "$RUN_ID" ;;
  stale)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('/usr/local/airflow/include/warehouse/training_dev.duckdb'); c.execute(\\\"update training_demo.holdings_raw set _extracted_at = now() - interval 2 day\\\"); print('custodian feed now looks 2 days old')\"" ;;
  fresh)
    inpod "$PY -c \"import duckdb; c=duckdb.connect('/usr/local/airflow/include/warehouse/training_dev.duckdb'); c.execute(\\\"update training_demo.holdings_raw set _extracted_at = now()\\\"); print('custodian feed stamped as fresh')\"" ;;
  *) sed -n '2,10p' "$0" ;;
esac
