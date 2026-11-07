"""portfolio_analytics_submit_run — the paved-path orchestration variant.

The same pipeline as portfolio_analytics_daily, but dbt runs INSIDE Databricks
as a Job rather than on the Airflow worker. Each Airflow task submits one step
to Databricks via DatabricksSubmitRunOperator and polls until it finishes.

When to prefer this over the Cosmos DbtTaskGroup variant:
  - the warehouse autoscales for the build, so the Airflow worker pool stays
    free for cross-system orchestration;
  - logs and artifacts live with the data in the Databricks Jobs UI;
  - one Airflow Connection, no dbt adapter on the worker.

Trade-off: you lose Cosmos's per-model task granularity — the Databricks Job is
one opaque step in the Airflow graph. This is the Capital Group paved path; the
Cosmos variant is what many dbt-centric shops use instead. Airflow schedules and
TRIGGERS the Databricks job; the job carries no Databricks-UI schedule.

CG note: this lab submits `notebook_task` steps to keep the payload readable.
The canonical CG execution model is a DAB `spark_python_task` invoking
`dbt_wrapper.py` (scrub sys.path, hydrate OAuth auth, `dbt deps|seed|run|test`,
tee logs + upload artifacts to a UC Volume) in a four-task layout
(deps -> seed -> run -> test). See Module 7 (CG Build Stack) for the wrapper.

Provider pin (Airflow 2.10 compatible):
    apache-airflow-providers-databricks>=7.4.0,<7.8.0
"""
from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.providers.databricks.operators.databricks import (
    DatabricksSubmitRunOperator,
)

from callbacks import on_failure_callback, on_sla_miss_callback

# Airflow Connection holding the workspace host + OAuth M2M service-principal
# credentials (DBX-SEC-002; PAT is forbidden in prod). Provisioned at the
# platform level; never embedded here.
DATABRICKS_CONN_ID = "databricks_default"

# A long-running interactive cluster keeps cold-start near zero. Swap to a
# `new_cluster` block in the payload for an isolated nightly job cluster.
DATABRICKS_EXISTING_CLUSTER_ID = "0501-060000-portfolio-prod"

# Workspace path holding the dbt-wrapping notebooks. Each notebook shells out
# to `dbt deps && dbt <command>` against the portfolio-analytics project that
# lives alongside it inside the workspace.
DBT_NOTEBOOK_BASE = "/Workspace/data-creators/dbt/portfolio_analytics"


default_args = {
    "owner": "portfolio-analytics-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=20),
    "on_failure_callback": on_failure_callback,
}


with DAG(
    dag_id="portfolio_analytics_submit_run",
    description=(
        "Paved-path variant: dbt runs inside Databricks as a Job. "
        "DatabricksSubmitRunOperator submits each step and polls."
    ),
    default_args=default_args,
    start_date=pendulum.datetime(2026, 5, 1, tz="Europe/London"),
    schedule="0 6 * * 1-5",
    catchup=False,
    max_active_runs=1,
    sla_miss_callback=on_sla_miss_callback,
    tags=["dbt", "portfolio-analytics", "databricks", "submit-run", "production", "usage-id:AA00002933", "cost-center:52415"],
    doc_md=__doc__,
) as dag:

    # Step 1 — source freshness. The notebook runs `dbt source freshness` and
    # exits non-zero if the custodian feed breaches error_after, failing the
    # task and short-circuiting the chain.
    check_source_freshness = DatabricksSubmitRunOperator(
        task_id="check_source_freshness",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "portfolio_analytics_source_freshness",
            "existing_cluster_id": DATABRICKS_EXISTING_CLUSTER_ID,
            "notebook_task": {
                "notebook_path": f"{DBT_NOTEBOOK_BASE}/check_source_freshness",
            },
        },
        polling_period_seconds=30,
        timeout_seconds=900,
    )

    # Step 2 — build all models (staging -> intermediate -> marts). Longer
    # timeout; carries the SLA so a slow build trips the sla_miss_callback.
    run_dbt_models = DatabricksSubmitRunOperator(
        task_id="run_dbt_models",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "portfolio_analytics_dbt_build",
            "existing_cluster_id": DATABRICKS_EXISTING_CLUSTER_ID,
            "notebook_task": {
                "notebook_path": f"{DBT_NOTEBOOK_BASE}/run_dbt_models",
            },
        },
        polling_period_seconds=60,
        timeout_seconds=3600,
        sla=timedelta(minutes=60),
    )

    # Step 3 — run every declared test (generic + the NAV reconciliation).
    test_dbt_models = DatabricksSubmitRunOperator(
        task_id="test_dbt_models",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "portfolio_analytics_dbt_test",
            "existing_cluster_id": DATABRICKS_EXISTING_CLUSTER_ID,
            "notebook_task": {
                "notebook_path": f"{DBT_NOTEBOOK_BASE}/test_dbt_models",
            },
        },
        polling_period_seconds=30,
        timeout_seconds=1800,
    )

    # Step 4 — refresh the docs catalog. Not on the data-delivery critical
    # path: a failure here does not block the published mart.
    generate_dbt_docs = DatabricksSubmitRunOperator(
        task_id="generate_dbt_docs",
        databricks_conn_id=DATABRICKS_CONN_ID,
        json={
            "run_name": "portfolio_analytics_dbt_docs",
            "existing_cluster_id": DATABRICKS_EXISTING_CLUSTER_ID,
            "notebook_task": {
                "notebook_path": f"{DBT_NOTEBOOK_BASE}/generate_dbt_docs",
            },
        },
        polling_period_seconds=30,
        timeout_seconds=900,
    )

    check_source_freshness >> run_dbt_models >> test_dbt_models >> generate_dbt_docs
