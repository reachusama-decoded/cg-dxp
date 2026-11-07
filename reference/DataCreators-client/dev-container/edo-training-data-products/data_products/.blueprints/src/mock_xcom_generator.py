def generate_mock_xcom(domain: str, model: str, **context):
    dag_run = context.get("dag_run")
    dag = context.get("dag")

    # Writes model name to dummy path to show ability to query model name from upstream
    try:
        from airflow.models import Variable
        current_path = Variable.get(
            "mock_current_path",
            default_var=f"s3://datalake-curated-dev-us-east-1/cspn_cons2/{model}/",
        )
        history_path = Variable.get(
            "mock_history_path",
            default_var=f"s3://datalake-curated-dev-us-east-1/cspn_cons2/{model}/partitiondate={context.get('ds', 'unknown')}/",
        )
    except Exception:
        current_path = f"s3://datalake-curated-dev-us-east-1/cspn_cons2/{model}/"
        history_path = f"s3://datalake-curated-dev-us-east-1/cspn_cons2/{model}/partitiondate={context.get('ds', 'unknown')}/"

    return {
        # --- identity ---
        "domain":        domain,
        "dataset":       model,
        "uuid":          dag_run.run_id if dag_run else context.get("run_id", "unknown-run-id"),
        "dataset_type":  "master",

        # --- S3 locations ---
        "current":       current_path,
        "history":       history_path,

        # --- operation metadata ---
        "operation_type":    "change",
        "app_cycle_date":    context.get("ds", "unknown"),
        "dlload_timestamp":  context.get("ts", "unknown"),
        "changed_data":      0,
    }
