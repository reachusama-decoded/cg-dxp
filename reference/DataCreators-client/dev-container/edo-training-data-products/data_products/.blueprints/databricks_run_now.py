from __future__ import annotations

import json
import logging

from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from blueprint import BaseModel, Blueprint, Field

logger = logging.getLogger(__name__)


def _databricks_failure_callback(context: dict) -> None:
    task_instance = context.get("task_instance")
    task = context.get("task")
    task_id = getattr(task, "task_id", "unknown")
    dag_id = getattr(task, "dag_id", "unknown")

    run_id = None
    if task_instance is not None:
        run_id = task_instance.xcom_pull(task_ids=task_id, key="run_id")
        if not run_id:
            run_id = task_instance.xcom_pull(task_ids=task_id, key="return_value")

    if not run_id:
        logger.warning(
            "Unable to pull Databricks logs for %s.%s because run_id is missing. "
            "Please click the Databricks logs link above to view logs directly in Databricks.",
            dag_id,
            task_id,
        )
        return

    databricks_conn_id = getattr(task, "databricks_conn_id", "caspian-training-databricks")

    try:
        from airflow.providers.databricks.hooks.databricks import DatabricksHook
    except Exception:
        logger.warning(
            "Unable to pull Databricks logs for %s.%s because DatabricksHook is unavailable. "
            "Please click the Databricks logs link above to view logs directly in Databricks.",
            dag_id,
            task_id,
        )
        return

    try:
        hook = DatabricksHook(databricks_conn_id=databricks_conn_id)
        run_details = hook.get_run(run_id=run_id)
        
        tasks = run_details.get("tasks", [])
        if tasks:
            failed_tasks = [t for t in tasks if t.get("state", {}).get("result_state") == "FAILED"]
            if not failed_tasks:
                failed_tasks = [t for t in tasks if t.get("state", {}).get("life_cycle_state") in ("INTERNAL_ERROR", "SKIPPED")]
            
            if failed_tasks:
                failed_task = failed_tasks[0]
                task_run_id = failed_task.get("run_id")
                task_key = failed_task.get("task_key", "unknown")
                logger.error("Databricks job has multiple tasks. Fetching output for failed task: %s (run_id=%s)", task_key, task_run_id)
                run_output = hook.get_run_output(run_id=task_run_id)
            else:
                run_output = {}
        else:
            run_output = hook.get_run_output(run_id=run_id)
    except Exception:
        logger.exception(
            "Databricks failure callback: failed to retrieve run output for %s.%s run_id=%s",
            dag_id,
            task_id,
            run_id,
        )
        return

    run_page_url = run_details.get("run_page_url")
    state = run_details.get("state", {})
    state_message = state.get("state_message")
    result_state = state.get("result_state")
    life_cycle_state = state.get("life_cycle_state")
    error_text = run_output.get("error")
    error_trace = run_output.get("error_trace")
    logs = run_output.get("logs")
    notebook_output = run_output.get("notebook_output", {})
    notebook_result = notebook_output.get("result")

    logger.error(
        "Databricks run failed for %s.%s run_id=%s conn_id=%s run_page_url=%s result_state=%s life_cycle_state=%s state_message=%s",
        dag_id,
        task_id,
        run_id,
        databricks_conn_id,
        run_page_url,
        result_state,
        life_cycle_state,
        state_message,
    )

    if error_text:
        logger.error("Databricks output error: %s", error_text)
    if error_trace:
        logger.error("Databricks output error_trace:\n%s", error_trace)
    if logs:
        logger.error("Databricks output logs:\n%s", logs)
    if notebook_result:
        logger.error("Databricks notebook result:\n%s", notebook_result)

    if not any([error_text, error_trace, logs, notebook_result]):
        logger.error(
            "Databricks output payload (no direct logs keys): %s",
            json.dumps(run_output, default=str)[:10000],
        )


class DatabricksRunNowConfig(BaseModel):
    job_name: str
    databricks_conn_id: str = Field(default="caspian-training-databricks")


class DatabricksRunNow(Blueprint[DatabricksRunNowConfig]):
    def render(self, config: DatabricksRunNowConfig) -> DatabricksRunNowOperator:
        return DatabricksRunNowOperator(
            task_id=self.step_id,
            job_name=config.job_name,
            databricks_conn_id=config.databricks_conn_id,
            deferrable=True,
            on_failure_callback=_databricks_failure_callback,
        )
