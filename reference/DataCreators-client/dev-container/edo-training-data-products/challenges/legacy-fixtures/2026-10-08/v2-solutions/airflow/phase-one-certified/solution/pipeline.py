from datetime import datetime, timedelta, timezone
from pathlib import Path
import json, os, subprocess
from airflow.sdk import dag, task
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / 'project'
def dbt_command(*args):
    executable = os.environ.get('V2_DBT_BIN', 'dbt')
    subprocess.run([executable, *args, '--project-dir', str(PROJECT), '--profiles-dir', str(PROJECT)], check=True)
@dag(dag_id='v2_training_pipeline', schedule=None, start_date=datetime(2025,1,1,tzinfo=timezone.utc), catchup=False, max_active_runs=1, tags=['v2-training','usage-id:AA00002933','cost-center:52415'], default_args={'retries':1,'retry_delay':timedelta(seconds=1)})
def pipeline():
    @task
    def prepare():
        dbt_command('seed')
    @task
    def build():
        dbt_command('run')
    @task
    def quality():
        if (ROOT / 'fail-quality').exists():
            raise ValueError('Intentional quality drill: remove fail-quality after diagnosis')
        dbt_command('test')
    @task
    def publish():
        from airflow.sdk import get_current_context
        conf=get_current_context()['dag_run'].conf or {}
        event=conf.get('event')
        if event:
            if event.get('dataset_id') != 'holdings' or event.get('dataset_version') != 'fixture-v1':
                raise ValueError('Event dataset does not identify the prepared fixture')
            if event.get('location') != 'fixture://holdings-v1':
                raise ValueError('Unknown dataset location; no arbitrary file execution')
        receipt={'run_id':get_current_context()['run_id'], 'event':event, 'model':'fund_exposure','expected_total':250}
        (ROOT / 'receipt.json').write_text(json.dumps(receipt,indent=2))
    prepare() >> build() >> quality() >> publish()
dag = pipeline()
