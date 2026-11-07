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
