"""Supplied smoke DAG; no CG domain, fee, temporal or blueprint solution behavior."""
import sys
from pathlib import Path

# Every CG product ships runtime/ and include/ packages; load only this product's copies.
ROOT = Path(__file__).resolve().parents[1]
for _name in [n for n in sys.modules if n.split('.')[0] in ('runtime', 'include')]:
    if not str(getattr(sys.modules[_name], '__file__', None) or '').startswith(str(ROOT) + '/'):
        del sys.modules[_name]
sys.path.insert(0, str(ROOT))

from datetime import datetime, timezone
from airflow.sdk import DAG, get_current_context
from airflow.providers.standard.operators.python import PythonOperator
from runtime.product import REQUIRED_TAGS, dag_id


def run_smoke():
    from runtime.tasks import smoke
    conf = get_current_context()['dag_run'].conf
    return smoke(conf['nonce'], conf['relation_prefix'], conf.get('connection_id', 'databricks_default'))


with DAG(dag_id('environment_smoke'), schedule=None, start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
         catchup=False, tags=['cg', 'environment', ROOT.name, *REQUIRED_TAGS]) as dag:
    PythonOperator(task_id='connected_smoke', python_callable=run_smoke)
