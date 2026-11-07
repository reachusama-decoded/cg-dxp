import os
import logging
import json
from pathlib import Path
import yaml

# The following import is here so Airflow parses this file
# from airflow import DAG
from dagfactory import load_yaml_dags

CONFIG_ROOT_DIR = Path(os.getenv("CONFIG_ROOT_DIR", str(Path(__file__).parent)))
GENERATED_DOC_MD_MARKER = "## Auto-Generated DAG Metadata"
logger = logging.getLogger(__name__)


def _iter_capsule_dag_configs() -> list[Path]:
    dag_files = list(CONFIG_ROOT_DIR.rglob("**/airflow/*.dag-factory.yml"))
    dag_files.extend(CONFIG_ROOT_DIR.rglob("**/airflow/*.dag-factory.yaml"))
    return sorted(dag_files)


def _data_product_tag_for_config(config_file: Path) -> str | None:
    try:
        relative_parts = config_file.relative_to(CONFIG_ROOT_DIR).parts
    except ValueError:
        return None

    if not relative_parts:
        return None

    return relative_parts[0]


def _dag_ids_with_explicit_doc_md(config_file: Path) -> set[str]:
    try:
        with config_file.open("r", encoding="utf-8") as config_stream:
            parsed_config = yaml.safe_load(config_stream)
    except (OSError, yaml.YAMLError):
        return set()

    if not isinstance(parsed_config, dict):
        return set()

    dag_ids: set[str] = set()
    for dag_id, dag_config in parsed_config.items():
        if dag_id == "default" or not isinstance(dag_config, dict):
            continue
        if "doc_md" in dag_config:
            dag_ids.add(str(dag_id))

    return dag_ids


def _tag_newly_loaded_dags(product_tag: str | None, before_keys: set[str]) -> None:
    if not product_tag:
        return

    for global_key in set(globals()) - before_keys:
        dag_obj = globals().get(global_key)
        if dag_obj is None or not hasattr(dag_obj, "dag_id") or not hasattr(dag_obj, "tags"):
            continue

        tags = list(dag_obj.tags or [])
        if product_tag not in tags:
            tags.append(product_tag)
            dag_obj.tags = tags


def _auto_generate_doc_md_if_missing(
    product_tag: str | None,
    dag_obj,
    config_file: Path,
    explicit_doc_md_dag_ids: set[str],
) -> None:
    if not product_tag:
        return

    dag_id = getattr(dag_obj, "dag_id", None)
    if not dag_id:
        return

    dag_id_str = str(dag_id)

    existing_doc = getattr(dag_obj, "doc_md", None)
    existing_doc_str = str(existing_doc) if existing_doc is not None else ""
    existing_doc_stripped = existing_doc_str.lstrip()
    if existing_doc_stripped.startswith(GENERATED_DOC_MD_MARKER):
        return

    schedule_value = getattr(dag_obj, "schedule_interval", None)
    if schedule_value is None:
        schedule_value = getattr(dag_obj, "schedule", None)

    default_args = getattr(dag_obj, "default_args", {}) or {}
    owner = default_args.get("owner", "")
    catchup = getattr(dag_obj, "catchup", "")

    try:
        source_config = str(config_file.relative_to(CONFIG_ROOT_DIR.parent))
    except ValueError:
        source_config = str(config_file)

    task_rows = []
    for task in getattr(dag_obj, "tasks", []):
        operator = task.__class__.__module__ + "." + task.__class__.__name__
        task_rows.append(f"| {task.task_id} | {operator} |")

    tasks_section = "\n".join(task_rows) if task_rows else "| _none_ | _none_ |"

    generated_doc_md = (
        f"{GENERATED_DOC_MD_MARKER}\n\n"
        f"# {dag_id_str}\n\n"
        "| Field | Value |\n"
        "| --- | --- |\n"
        f"| Data Product | {product_tag} |\n"
        f"| DAG ID | {dag_id_str} |\n"
        f"| Source Config | {source_config} |\n"
        f"| Owner | {owner} |\n"
        f"| Schedule | {schedule_value} |\n"
        f"| Catchup | {catchup} |\n\n"
        "## Tasks\n\n"
        "| Task ID | Operator |\n"
        "| --- | --- |\n"
        f"{tasks_section}\n"
    )

    if dag_id_str in explicit_doc_md_dag_ids and existing_doc_str.strip():
        dag_obj.doc_md = f"{generated_doc_md}\n\n---\n\n{existing_doc_str}"
        return

    dag_obj.doc_md = generated_doc_md


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


def _attach_databricks_failure_callback_if_missing(dag_obj) -> None:
    for task in getattr(dag_obj, "tasks", []):
        operator_module = task.__class__.__module__
        operator_name = task.__class__.__name__
        is_databricks_run_now_operator = (
            "airflow.providers.databricks" in operator_module
            and operator_name == "DatabricksRunNowOperator"
        )
        if not is_databricks_run_now_operator:
            continue

        if getattr(task, "on_failure_callback", None):
            continue

        task.on_failure_callback = _databricks_failure_callback

for config_file in _iter_capsule_dag_configs():
    before_load_keys = set(globals())
    explicit_doc_md_dag_ids = _dag_ids_with_explicit_doc_md(config_file)
    try:
        load_yaml_dags(
            globals_dict=globals(),
            config_filepath=str(config_file),
        )
    except Exception:
        logger.exception("Failed to load DAG config: %s", config_file)
        continue

    product_tag = _data_product_tag_for_config(config_file)
    _tag_newly_loaded_dags(
        product_tag=product_tag,
        before_keys=before_load_keys,
    )

    for global_key in set(globals()) - before_load_keys:
        dag_obj = globals().get(global_key)
        if dag_obj is None or not hasattr(dag_obj, "dag_id"):
            continue
        _attach_databricks_failure_callback_if_missing(dag_obj)
        _auto_generate_doc_md_if_missing(
            product_tag=product_tag,
            dag_obj=dag_obj,
            config_file=config_file,
            explicit_doc_md_dag_ids=explicit_doc_md_dag_ids,
        )