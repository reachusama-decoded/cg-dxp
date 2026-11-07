"""portfolio_analytics_daily — challenge stub.

Trainees wire the freshness -> dbt_pipeline -> publish chain here.
"""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from callbacks import (
    on_failure_callback,
    on_retry_callback,
    on_sla_miss_callback,
    on_success_callback,
)
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig
from cosmos.config import RenderConfig, TestBehavior

DBT_PROJECT_DIR = Path(__file__).resolve().parents[1] / "dbt"
# The Astro image installs dbt in an isolated venv (requirements-venv-cosmos.txt)
# so its deps do not clash with Airflow; point Cosmos at that dbt executable.
DBT_EXECUTABLE_PATH = os.environ.get(
    "COSMOS_DBT_EXECUTABLE_PATH", "/home/astro/.venv/cosmos/bin/dbt"
)


def _build_dbt_runtime_env() -> dict[str, str]:
    """Best-effort env for non-interactive Databricks auth in local Airflow.

    Uses `databricks_default` when available, but never fails DAG import if the
    runtime context cannot resolve the connection.
    """
    env: dict[str, str] = {}
    try:
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection("databricks_default")
        if conn.host:
            env["DATABRICKS_HOST"] = conn.host.replace("https://", "").replace("http://", "").rstrip("/")
        if conn.password:
            env["DBT_ACCESS_TOKEN"] = conn.password
    except Exception:
        # Keep DAG import parse-safe in contexts where connection lookup is unavailable.
        pass
    return env


# Why NOT `DBT_RUNTIME_ENV = _build_dbt_runtime_env()` at module level: that runs at DAG
# PARSE time and bakes the live OAuth token into every Cosmos task's serialized
# definition. The token is rotated periodically, so each rotation changed the serialized
# DAG and made Airflow record a NEW DAG version -- 41 versions accumulated here, 8 of them
# holding distinct real tokens in the metadata database. The Airflow UI renders a run
# against a DAG version, so tasks from a mismatched version appear in the grid with no
# task instance behind them and 404 when clicked.
# `env` is a Cosmos template field, so a Jinja string stays CONSTANT in the serialized DAG
# and resolves to the current credential at task run time instead.
DBT_TEMPLATED_ENV = {
    "DATABRICKS_HOST": (
        "{{ conn.databricks_default.host | replace('https://', '') | replace('http://', '') }}"
    ),
    "DBT_ACCESS_TOKEN": "{{ conn.databricks_default.password }}",
}


def _check_source_freshness() -> None:
    """Fail the run if the custodian feed is stale.

    Runs `dbt source freshness` and raises on a non-zero exit, so a breach of the
    source's error_after threshold fails this task and short-circuits the DAG.
    A PythonOperator wraps this because CG governance (Cimon) blocks operators
    that execute arbitrary shell (BashOperator, SSHOperator, ...).
    """
    import subprocess

    freshness_env = os.environ.copy()
    # Resolved here, at task run time -- see the note on DBT_TEMPLATED_ENV for why this
    # must not be computed once at DAG parse time.
    freshness_env.update(_build_dbt_runtime_env())
    target = "airflow" if freshness_env.get("DBT_ACCESS_TOKEN") else "dev"

    # Prefer pulling host/token from Airflow connection when available, but do
    # not fail if the connection backend is temporarily unavailable in runtime
    # task context (observed intermittently in Airflow 3 local dags test).
    try:
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection("databricks_default")
        freshness_env["DATABRICKS_HOST"] = (
            (conn.host or freshness_env.get("DATABRICKS_HOST", ""))
            .replace("https://", "")
            .replace("http://", "")
            .rstrip("/")
        )
        if conn.password:
            freshness_env["DBT_ACCESS_TOKEN"] = conn.password
            target = "airflow"
    except Exception:
        # Fallback to OAuth profile target that reads env + ~/.databrickscfg.
        target = "dev"

    completed = subprocess.run(
        [
            DBT_EXECUTABLE_PATH,
            "source",
            "freshness",
            "--select",
            "source:custodian",
            "--project-dir",
            DBT_PROJECT_DIR.as_posix(),
            "--profiles-dir",
            DBT_PROJECT_DIR.as_posix(),
            "--target",
            target,
        ],
        env=freshness_env,
        check=False,
        capture_output=True,
        text=True,
    )
    output = f"{completed.stdout or ''}{completed.stderr or ''}"
    print(output)  # Why: dbt's own output is the real diagnostic; surface it in the task log.
    if completed.returncode != 0:
        # Why: dbt exits non-zero for BOTH a real freshness breach AND a Databricks
        # connection/config error (e.g. no http_path when the astro stack was started
        # before `mise run setup:databricks` populated the env — the common cold start).
        # Report them differently so a trainee is not sent chasing a stale feed on a cold start.
        connection_error = any(
            marker in output
            for marker in ("http_path", "Could not connect", "Invalid IPv6 URL", "Runtime Error")
        )
        if connection_error:
            raise RuntimeError(
                "dbt could not connect to Databricks (e.g. missing http_path). This usually "
                "means the astro stack started before your Databricks env was ready. From the "
                "devcontainer, wait for `mise run setup:databricks` to finish, then run "
                "`astro dev restart` and re-run this task.\n" + output[-2000:]
            )
        raise RuntimeError(
            "dbt source freshness failed: the custodian feed breached its error_after "
            "threshold. Refresh the feed with `mise run challenge:seed 02`, then re-run.\n"
            + output[-2000:]
        )


def _publish_to_catalog() -> None:
    """Stand in for catalog grants + downstream notify."""
    print("[publish] catalog grants + downstream notify")


profile_config = ProfileConfig(
    profile_name="portfolio_analytics",
    target_name="dev",
    # Use the repo profile directly to avoid runtime lookups via BaseHook in
    # Airflow 3 task-execution context, which can intermittently fail to resolve
    # connection metadata during local `astro dev run dags test` runs.
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
    description="Challenge stub for the portfolio analytics orchestration DAG.",
    default_args=default_args,
    start_date=pendulum.datetime(2026, 5, 1, tz="Europe/London"),
    schedule="0 6 * * 1-5",
    catchup=False,
    max_active_runs=1,
    # Why 4: the five staging models have no interdependencies, so serialising every
    # task (max_active_tasks=1) made a full run take ~4 minutes for work the warehouse
    # can overlap. 4 keeps a laptop devcontainer comfortable while removing most of
    # the wait; max_active_runs=1 still prevents two runs racing on the same tables.
    max_active_tasks=4,
    sla_miss_callback=on_sla_miss_callback,
    tags=["dbt", "portfolio-analytics", "cosmos", "databricks", "training", "usage-id:AA00002933", "cost-center:52415"],
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
        # Run tests after all model builds so relationship tests don't reference
        # downstream marts before those relations exist.
        render_config=RenderConfig(test_behavior=TestBehavior.AFTER_ALL),
        operator_args={
            "install_deps": True,
            "append_env": True,
            "env": DBT_TEMPLATED_ENV,
        },
    )

    publish_to_catalog = PythonOperator(
        task_id="publish_to_catalog",
        python_callable=_publish_to_catalog,
        sla=timedelta(minutes=90),
        on_success_callback=on_success_callback,
    )

    end = EmptyOperator(task_id="end")

    # TODO: wire start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end
