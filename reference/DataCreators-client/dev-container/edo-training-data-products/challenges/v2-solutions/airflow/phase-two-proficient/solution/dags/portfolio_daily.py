"""Scheduled Portfolio Analytics evidence; no production publication.
Prepared for the supplied Airflow 3/standard-provider boundary; live imports pending.
"""
from datetime import timedelta
from pathlib import Path
import json, os
import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
ROOT = Path(__file__).resolve().parents[1]
OWNER = json.loads((ROOT / "ownership.json").read_text())
PREFIX = OWNER["prefix"]
PROJECT = ROOT / "project"
DBT = os.environ.get("DC_WORKER_DBT_BIN", "/home/astro/.venv/cosmos/bin/dbt")

def callback(context):
    import logging
    logging.getLogger(__name__).error("Portfolio task failed: %s", context.get("task_instance"))

def work(step, runtime_env, partition, run_id, logical_date):
    import importlib.util, subprocess
    if partition not in {"2026-05-20", "2026-05-21"}:
        raise ValueError("Unsupported holdings business date")
    configured_host=OWNER["config"]["DATABRICKS_HOST"].removeprefix("https://").removeprefix("http://").rstrip("/")
    actual_host=runtime_env["DATABRICKS_HOST"].removeprefix("https://").removeprefix("http://").rstrip("/")
    if actual_host != configured_host: raise ValueError("Worker connection does not match the terminal source-loading host")
    env = {**os.environ, **runtime_env}
    spec = importlib.util.spec_from_file_location("portfolio_runtime", ROOT / "runtime/lab.py")
    runtime = importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)
    # Each worker task resolves templated credentials at execution, then runs its own process.
    # The worker is shared; no credentials are written into a manifest or receipt.
    os.environ.update(runtime_env)
    if step == "source_ready":
        cfg = runtime.configuration()
        for name,count in [("holdings_raw",8),("positions_raw",8),("prices_raw",8),("fx_rates_raw",6),("fund_master_raw",4),("refdata_raw",4)]:
            result=runtime.query(f"select count(*) from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{PREFIX}_{name}`")
            if result != [[count]]: raise ValueError("Source population differs: " + name)
        command = [DBT,"source","freshness"]
    elif step == "dbt_build":
        command = [DBT,"build"]
    elif step == "quality":
        if (ROOT / "fail-quality").exists(): raise ValueError("Intentional Portfolio quality drill")
        runtime.check(PROJECT,"portfolio")
        return {"partition":partition,"run_id":run_id}
    elif step == "publication_evidence":
        evidence=runtime.check(PROJECT,"portfolio")
        cfg=runtime.configuration()
        selected=runtime.query(f"select fund_id,position_date,holdings,exposure_gbp,nav_per_unit from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{PREFIX}_fund_nav_report` where position_date = '{partition}' order by fund_id")
        expected=[r for r in runtime.portfolio(PROJECT/"seeds") if r[1]==partition]
        if len(selected)!=4 or [[str(v) for v in r[:3]] for r in selected]!=[[str(v) for v in r[:3]] for r in expected]: raise ValueError("Partition key population differs")
        evidence["partition_rows"]=[[str(v) for v in row] for row in selected]
        evidence.update({"run_id":run_id,"partition":partition,"logical_date":logical_date,"input_sha256":{p.name:runtime.digest(p) for p in sorted((PROJECT/"seeds").glob("*.csv"))}})
        runtime.write(ROOT / "evidence" / (run_id.replace(":","_").replace("/","_")+".json"),evidence)
        return {"partition":partition,"run_id":run_id}
    else: raise ValueError("Unknown step")
    subprocess.run(command+["--project-dir",str(PROJECT),"--profiles-dir",str(PROJECT),"--target","airflow","--target-path",str(PROJECT/"target")],env=env,check=True)
    return {"partition":partition,"run_id":run_id}

RUNTIME_ENV = {
    "DATABRICKS_HOST": "{{ conn.databricks_default.host | replace('https://', '') | replace('http://', '') }}",
    "DBT_ACCESS_TOKEN": "{{ conn.databricks_default.password }}",
    "DATABRICKS_HTTP_PATH": OWNER["config"]["DATABRICKS_HTTP_PATH"],
    "DBT_CATALOG": OWNER["config"]["DBT_CATALOG"],
    "DBT_SCHEMA": OWNER["config"]["DBT_SCHEMA"],
    "DC_RELATION_PREFIX": PREFIX,
}
with DAG(
    dag_id=PREFIX+"_portfolio_daily",
    start_date=pendulum.datetime(2026,10,8,tz="Europe/London"),
    schedule=timedelta(minutes=2), catchup=False, max_active_runs=1,
    params={"fixture_partition":"2026-05-20"},
    default_args={"owner":"training","retries":1,"retry_delay":timedelta(minutes=1),"on_failure_callback":callback},
    tags=["training","databricks","portfolio-analytics","usage-id:AA00002933","cost-center:52415"],
) as dag:
    tasks={name:PythonOperator(task_id=name,python_callable=work,op_kwargs={
        "step":name,"runtime_env":RUNTIME_ENV,"partition":"{{ params.fixture_partition }}",
        "run_id":"{{ run_id }}","logical_date":"{{ logical_date }}",
    }) for name in ["source_ready","dbt_build","quality","publication_evidence"]}
    tasks["source_ready"] >> tasks["dbt_build"] >> tasks["quality"] >> tasks["publication_evidence"]
