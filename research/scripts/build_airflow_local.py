#!/usr/bin/env python3
"""Generate the Day 4 Astro project: courseware/day4-airflow/demos/airflow_local/.
Same image family, Cosmos version and dbt venv path as the learners' container; DuckDB in
place of Databricks. The dbt projects are copied from the Day 3 and Day 2 demos."""
import pathlib, shutil, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIENT = ROOT / "reference/DataCreators-client/dev-container/edo-training-data-products"
SOL = CLIENT / "challenges/v1/03-airflow-orchestration/solution"
PA = ROOT / "courseware/day3-dbt/demos/portfolio_analytics"
EOD = ROOT / "courseware/day2-platform/demos/contract-to-code/eod_prices"
DST = ROOT / "courseware/day4-airflow/demos/airflow_local"
if DST.exists():
    shutil.rmtree(DST)
IGN = shutil.ignore_patterns("target", "warehouse", "logs", "dbt_packages", "demo.sh", "run.sh", ".gitignore", "*.pyc")
(DST / "dags/portfolio_analytics/dags").mkdir(parents=True)
(DST / "dags/eod_prices/dags").mkdir(parents=True)
(DST / "include/warehouse").mkdir(parents=True)
(DST / "plugins").mkdir(); (DST / "tests").mkdir(); (DST / ".astro").mkdir()
shutil.copytree(PA, DST / "dags/portfolio_analytics/dbt", ignore=IGN)
shutil.copytree(EOD, DST / "dags/eod_prices/dbt", ignore=IGN)
# the learners' callbacks and alert transport, imported as siblings of the DAG file
cb = (SOL / "dags/callbacks.py").read_text().replace("from include.alerting.notifications import send_alert", "from notifications import send_alert")
(DST / "dags/portfolio_analytics/dags/callbacks.py").write_text(cb)
shutil.copy(SOL / "include/alerting/notifications.py", DST / "dags/portfolio_analytics/dags/notifications.py")
for rel in ["include/monitoring/portfolio_analytics.yml", "include/runbooks/portfolio_analytics.md", "include/launch/consumer-guide.md"]:
    (DST / "dags/portfolio_analytics" / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SOL / rel, DST / "dags/portfolio_analytics" / rel)
(DST / "include/warehouse/.gitkeep").write_text("")

def w(rel, text):
    p = DST / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip("\n"))

w("dags/portfolio_analytics/dags/portfolio_analytics_daily.py", '''
    """portfolio_analytics_daily — orchestrate the portfolio-analytics dbt build.

    Instructor demo copy of the learners' challenge-03 solution. Same topology:

        start
          -> source_freshness_check     (fail fast on a stale custodian feed)
          -> dbt_pipeline               (Cosmos DbtTaskGroup over ../dbt: one task per model and test)
          -> publish_to_catalog         (SLA + success notification)
          -> end

    Differences from the learners' version, all deliberate:
      * the warehouse is a DuckDB file under include/warehouse/ instead of Databricks, so
        dbt-duckdb sits in the cosmos venv at the same path (/home/astro/.venv/cosmos/bin/dbt);
      * max_active_tasks=1 because a DuckDB file has one writer; Databricks allows 4;
      * callbacks.py and notifications.py sit beside this file and are imported directly.
    """
    from __future__ import annotations

    import os
    import subprocess
    import sys
    from datetime import timedelta
    from pathlib import Path

    import pendulum
    from airflow import DAG
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.python import PythonOperator

    HERE = Path(__file__).resolve().parent
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))

    from callbacks import (  # noqa: E402
        on_failure_callback,
        on_retry_callback,
        on_sla_miss_callback,
        on_success_callback,
    )
    from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig  # noqa: E402
    from cosmos.config import RenderConfig, TestBehavior  # noqa: E402

    DBT_PROJECT_DIR = HERE.parent / "dbt"
    DBT_EXECUTABLE_PATH = os.environ.get("COSMOS_DBT_EXECUTABLE_PATH", "/home/astro/.venv/cosmos/bin/dbt")
    DBT_ENV = {
        "PA_DUCKDB_PATH": os.environ.get("PA_DUCKDB_PATH", "/usr/local/airflow/include/warehouse/training_dev.duckdb"),
        "PA_SCHEMA": os.environ.get("PA_SCHEMA", "training_demo"),
    }


    def _run_dbt(*args: str) -> subprocess.CompletedProcess:
        cmd = [DBT_EXECUTABLE_PATH, *args, "--project-dir", DBT_PROJECT_DIR.as_posix(),
               "--profiles-dir", DBT_PROJECT_DIR.as_posix(), "--target", "local"]
        env = {**os.environ, **DBT_ENV}
        completed = subprocess.run(cmd, env=env, check=False, capture_output=True, text=True)
        print(f"$ {' '.join(cmd)}")
        print(completed.stdout or "", completed.stderr or "")
        return completed


    def _check_source_freshness() -> None:
        """Fail the run if the custodian feed is stale (its error_after threshold is breached).

        `dbt source freshness` exits non-zero on a breach; raising here fails this task and
        short-circuits the DAG before any build compute is spent. PythonOperator, not
        BashOperator: CG governance blocks arbitrary-shell operators.
        """
        completed = _run_dbt("source", "freshness", "--select", "source:custodian")
        if completed.returncode != 0:
            raise RuntimeError(
                "dbt source freshness failed: the custodian feed breached its error_after "
                "threshold. Refresh the feed (bash run.sh fresh) and re-run."
            )


    def _publish_to_catalog() -> None:
        """Stand-in for catalog grants + downstream notify: show what was published."""
        completed = _run_dbt("show", "--select", "agg_fund_daily_exposure", "--limit", "8")
        if completed.returncode != 0:
            raise RuntimeError("could not read the published mart")
        print("[publish] catalog grants + downstream notify")


    profile_config = ProfileConfig(
        profile_name="portfolio_analytics_challenge",
        target_name="local",
        profiles_yml_filepath=(DBT_PROJECT_DIR / "profiles.yml").as_posix(),
    )

    default_args = {
        "owner": "portfolio-analytics-team",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=20),
        "on_failure_callback": on_failure_callback,
        "on_retry_callback": on_retry_callback,
    }

    with DAG(
        dag_id="portfolio_analytics_daily",
        description=(
            "Daily refresh of the Client Portfolio Analytics product. "
            "SLA: mart published by 07:30 UK from a 06:00 UK weekday schedule."
        ),
        default_args=default_args,
        start_date=pendulum.datetime(2026, 5, 1, tz="Europe/London"),
        schedule="0 6 * * 1-5",
        catchup=False,
        max_active_runs=1,
        max_active_tasks=1,
        sla_miss_callback=on_sla_miss_callback,
        tags=["dbt", "portfolio-analytics", "cosmos", "duckdb", "training",
              "usage-id:AA00002933", "cost-center:52415"],
        doc_md=__doc__,
    ) as dag:
        start = EmptyOperator(task_id="start")

        source_freshness_check = PythonOperator(
            task_id="source_freshness_check",
            python_callable=_check_source_freshness,
        )

        dbt_pipeline = DbtTaskGroup(
            group_id="dbt_pipeline",
            project_config=ProjectConfig(DBT_PROJECT_DIR.as_posix()),
            profile_config=profile_config,
            execution_config=ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH),
            render_config=RenderConfig(test_behavior=TestBehavior.AFTER_ALL, exclude=["tag:stretch"]),
            operator_args={"install_deps": False, "append_env": True, "env": DBT_ENV},
        )

        publish_to_catalog = PythonOperator(
            task_id="publish_to_catalog",
            python_callable=_publish_to_catalog,
            sla=timedelta(minutes=90),
            on_success_callback=on_success_callback,
        )

        end = EmptyOperator(task_id="end")

        start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end
    ''')

w("dags/eod_prices/dags/eod_prices_daily.py", '''
    """eod_prices_daily — the Day 2 contract-to-code product, orchestrated.

    What the running-example contract promises, as configuration: a 06:30 America/New_York
    weekday schedule so the US price sheet is published by 07:30 ET; a freshness gate on the
    vendor feed; the dbt build (models, then tests) as a Cosmos task group; a publish step.
    """
    from __future__ import annotations

    import os
    import subprocess
    from datetime import timedelta
    from pathlib import Path

    import pendulum
    from airflow import DAG
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.python import PythonOperator
    from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig
    from cosmos.config import RenderConfig, TestBehavior

    DBT_PROJECT_DIR = Path(__file__).resolve().parents[1] / "dbt"
    DBT_EXECUTABLE_PATH = os.environ.get("COSMOS_DBT_EXECUTABLE_PATH", "/home/astro/.venv/cosmos/bin/dbt")
    DBT_ENV = {
        "EOD_DUCKDB_PATH": os.environ.get("EOD_DUCKDB_PATH", "/usr/local/airflow/include/warehouse/eod_prices.duckdb"),
        "EOD_SCHEMA": os.environ.get("EOD_SCHEMA", "training_demo"),
    }


    def _run_dbt(*args: str) -> subprocess.CompletedProcess:
        cmd = [DBT_EXECUTABLE_PATH, *args, "--project-dir", DBT_PROJECT_DIR.as_posix(),
               "--profiles-dir", DBT_PROJECT_DIR.as_posix(), "--target", "local"]
        completed = subprocess.run(cmd, env={**os.environ, **DBT_ENV}, check=False, capture_output=True, text=True)
        print(f"$ {' '.join(cmd)}"); print(completed.stdout or "", completed.stderr or "")
        return completed


    def _check_vendor_freshness() -> None:
        if _run_dbt("source", "freshness", "--select", "source:vendor_feed").returncode != 0:
            raise RuntimeError("vendor feed stale: error_after breached; do not build the price sheet")


    def _publish() -> None:
        if _run_dbt("show", "--select", "rpt_eod_prices_us", "--limit", "10").returncode != 0:
            raise RuntimeError("could not read rpt_eod_prices_us")
        print("[publish] price sheet published; consumer notified")


    with DAG(
        dag_id="eod_prices_daily",
        description="US end-of-day price sheet in USD; contract SLA: published by 07:30 ET on US business days.",
        default_args={"owner": "pricing-data-team", "retries": 1, "retry_delay": timedelta(minutes=5)},
        start_date=pendulum.datetime(2026, 11, 1, tz="America/New_York"),
        schedule="30 6 * * 1-5",
        catchup=False,
        max_active_runs=1,
        max_active_tasks=1,
        tags=["dbt", "eod-prices", "cosmos", "duckdb", "training", "usage-id:AA00002933", "cost-center:52415"],
        doc_md=__doc__,
    ) as dag:
        start = EmptyOperator(task_id="start")
        vendor_freshness_check = PythonOperator(task_id="vendor_freshness_check", python_callable=_check_vendor_freshness)
        dbt_pipeline = DbtTaskGroup(
            group_id="dbt_pipeline",
            project_config=ProjectConfig(DBT_PROJECT_DIR.as_posix()),
            profile_config=ProfileConfig(profile_name="eod_prices", target_name="local",
                                         profiles_yml_filepath=(DBT_PROJECT_DIR / "profiles.yml").as_posix()),
            execution_config=ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH),
            render_config=RenderConfig(test_behavior=TestBehavior.AFTER_ALL),
            operator_args={"install_deps": False, "append_env": True, "env": DBT_ENV},
        )
        publish_price_sheet = PythonOperator(task_id="publish_price_sheet", python_callable=_publish)
        end = EmptyOperator(task_id="end")

        start >> vendor_freshness_check >> dbt_pipeline >> publish_price_sheet >> end
    ''')

w("Dockerfile", """
    # Same image family as the learners' container (astro-runtime 3.1-17-base = Airflow 3.1.8,
    # Python 3.12), same split: Airflow providers in the base environment, dbt in its own venv
    # at /home/astro/.venv/cosmos so Cosmos finds it at the same path.
    FROM quay.io/astronomer/astro-runtime:3.1-17-base

    USER root
    COPY requirements.txt /tmp/requirements.txt
    RUN pip install --no-cache-dir -r /tmp/requirements.txt

    USER astro
    COPY requirements-venv-cosmos.txt /tmp/requirements-venv-cosmos.txt
    RUN python3 -m venv /home/astro/.venv/cosmos \\
        && /home/astro/.venv/cosmos/bin/python -m pip install --no-cache-dir --upgrade pip \\
        && /home/astro/.venv/cosmos/bin/python -m pip install --no-cache-dir -r /tmp/requirements-venv-cosmos.txt
    """)
w("requirements.txt", """
    # Pinned as in the learners' image (requirements-pypi.txt): Cosmos renders the dbt project
    # as Airflow tasks; the http provider carries the Teams-webhook alert transport.
    astronomer-cosmos==1.15.0
    apache-airflow-providers-http==5.4.0
    """)
w("requirements-venv-cosmos.txt", """
    # /home/astro/.venv/cosmos — dbt in its own venv, as in the learners' image, with the
    # DuckDB adapter in place of dbt-databricks. dbt-core pinned to the dev container's 1.11.8.
    dbt-core==1.11.8
    dbt-duckdb==1.11.1
    """)
w("packages.txt", "# No OS packages needed for the demo.\n")
w(".dockerignore", "include/warehouse\n**/target\n**/logs\n**/warehouse\n**/dbt_packages\n.git\n")
w(".gitignore", "include/warehouse/*.duckdb\n**/target/\n**/logs/\n**/dbt_packages/\nairflow_settings.yaml\n.env\n")
w(".astro/config.yaml", """
    project:
        name: portfolio-analytics-demo
    """)
w("airflow_settings.yaml", """
    # Local-only Airflow objects imported by `astro dev start`. No secrets here.
    # The DAG's send_alert() posts to an HTTP connection named alert_webhook; when it is
    # absent the transport logs a warning instead of failing the task (see notifications.py).
    airflow:
      connections: []
      pools: []
      variables: []
    """)
w("docker-compose.override.yml", """
    # Merged into the compose file the Astro CLI generates (same mechanism as the learners'
    # repo). Points dbt at the DuckDB files under include/warehouse and keeps telemetry off.
    x-airflow-common: &airflow-common
      environment:
        PA_DUCKDB_PATH: /usr/local/airflow/include/warehouse/training_dev.duckdb
        PA_SCHEMA: training_demo
        EOD_DUCKDB_PATH: /usr/local/airflow/include/warehouse/eod_prices.duckdb
        EOD_SCHEMA: training_demo
        AIRFLOW__CORE__LOAD_EXAMPLES: "False"
        AIRFLOW__LOGGING__REMOTE_LOGGING: "False"
        ASTRO_DATADOG_TASK_LOGS_ENABLED: "false"
        AIRFLOW__METRICS__STATSD_DATADOG_ENABLED: "false"
        AIRFLOW__SECRETS__BACKEND: "airflow.secrets.metastore.MetastoreBackend"
        AIRFLOW__SECRETS__BACKEND_KWARGS: "{}"
        AIRFLOW__CORE__TEST_CONNECTION: "Enabled"

    services:
      dag-processor:
        <<: *airflow-common
      scheduler:
        <<: *airflow-common
      triggerer:
        <<: *airflow-common
      api-server:
        <<: *airflow-common
    """)
w("run.sh", """
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
        inpod "$PY -c \\"import duckdb; c=duckdb.connect('/usr/local/airflow/include/warehouse/training_dev.duckdb'); c.execute(\\\\\\"update training_demo.holdings_raw set _extracted_at = now() - interval 2 day\\\\\\"); print('custodian feed now looks 2 days old')\\"" ;;
      fresh)
        inpod "$PY -c \\"import duckdb; c=duckdb.connect('/usr/local/airflow/include/warehouse/training_dev.duckdb'); c.execute(\\\\\\"update training_demo.holdings_raw set _extracted_at = now()\\\\\\"); print('custodian feed stamped as fresh')\\"" ;;
      *) sed -n '2,10p' "$0" ;;
    esac
    """)
(DST / "run.sh").chmod(0o755)
print("written", DST)
