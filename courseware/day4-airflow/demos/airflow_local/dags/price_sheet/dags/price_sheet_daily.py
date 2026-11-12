"""price_sheet_daily: Day 3's price sheet, run by Airflow.

The instructor's demo DAG for Day 4, in the same shape as the learners' challenge-03 DAG:

    start
      -> source_freshness_check     (fail fast when the vendor price feed is stale)
      -> dbt_pipeline               (Cosmos DbtTaskGroup over ../dbt: one task per model, then the tests)
      -> publish_to_catalog         (carries the SLA and the success notification)
      -> end

Differences from the learners' DAG, all deliberate:
  * the warehouse is a DuckDB file under include/warehouse/, not Databricks;
  * max_active_tasks=1, because a DuckDB file takes one writer (the learners' DAG has 4);
  * retry_delay is 15 seconds, not 2 minutes, so a failure shows yellow, yellow, red inside a minute;
  * callbacks.py and notifications.py sit beside this file.
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


def _run_dbt(*args: str) -> subprocess.CompletedProcess:
    cmd = [DBT_EXECUTABLE_PATH, *args, "--project-dir", DBT_PROJECT_DIR.as_posix(),
           "--profiles-dir", DBT_PROJECT_DIR.as_posix(), "--target", "local"]
    completed = subprocess.run(cmd, env={**os.environ}, check=False, capture_output=True, text=True)
    print(f"$ {' '.join(cmd)}")
    print(completed.stdout or "", completed.stderr or "")
    return completed


def _check_source_freshness() -> None:
    """Fail the run when the vendor price feed is older than its error_after threshold.

    `dbt source freshness` exits non-zero on a breach; raising here fails this task, and nothing
    downstream runs. A PythonOperator, not a BashOperator: CG governance blocks operators that run
    arbitrary shell.
    """
    completed = _run_dbt("source", "freshness", "--select", "source:vendor_feed")
    if completed.returncode != 0:
        raise RuntimeError(
            "dbt source freshness failed: the vendor price feed breached its error_after threshold."
        )


def _publish_to_catalog() -> None:
    """Stand-in for the catalog grants and the consumer notification: show what was published."""
    completed = _run_dbt("show", "--select", "fct_prices_usd", "--limit", "8")
    if completed.returncode != 0:
        raise RuntimeError("could not read the published price sheet")
    print("[publish] catalog grants + downstream notify")


profile_config = ProfileConfig(
    profile_name="price_sheet",
    target_name="local",
    profiles_yml_filepath=(DBT_PROJECT_DIR / "profiles.yml").as_posix(),
)

default_args = {
    "owner": "pricing-data-team",                  # who is responsible; shown in the Airflow UI
    "retries": 2,                                  # two more tries after a failure: three attempts in all
    "retry_delay": timedelta(seconds=15),          # wait before the first retry (the learners' DAG: timedelta(minutes=2))
    "retry_exponential_backoff": True,             # each wait is longer than the last, roughly doubling
    "max_retry_delay": timedelta(minutes=20),      # the longest the backoff wait can grow to
    "on_failure_callback": on_failure_callback,    # called when a task has used its retries and failed
    "on_retry_callback": on_retry_callback,        # called each time a task fails and is about to retry
}

with DAG(
    dag_id="price_sheet_daily",
    description="Daily refresh of the price sheet. SLA: published by 07:30 UK from a 06:00 UK weekday schedule.",
    default_args=default_args,
    start_date=pendulum.datetime(2026, 11, 1, tz="Europe/London"),
    schedule="0 6 * * 1-5",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    sla_miss_callback=on_sla_miss_callback,
    tags=["dbt", "price-sheet", "cosmos", "duckdb", "training"],
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
        # Models and tests only: the raw feeds are delivered from outside (here: bash run.sh seed), not by this DAG.
        render_config=RenderConfig(test_behavior=TestBehavior.AFTER_ALL, exclude=["resource_type:seed"]),
        operator_args={"install_deps": False, "append_env": True},
    )

    publish_to_catalog = PythonOperator(
        task_id="publish_to_catalog",
        python_callable=_publish_to_catalog,
        sla=timedelta(minutes=90),
        on_success_callback=on_success_callback,
    )

    end = EmptyOperator(task_id="end")

    start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end
