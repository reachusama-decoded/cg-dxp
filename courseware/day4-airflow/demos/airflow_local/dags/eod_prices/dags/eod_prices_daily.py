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
