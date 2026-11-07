"""Real Airflow import and execution; run only in an isolated AIRFLOW_HOME."""
import importlib.util, json, sys
from pathlib import Path
from airflow.models import DagBag
from airflow.utils.state import DagRunState
w=Path(sys.argv[1]);starter=sys.argv[2]=='starter'
bag=DagBag(dag_folder=str(w/'pipeline.py'),include_examples=False)
assert not bag.import_errors,bag.import_errors
assert len(bag.dags)==1,bag.dags.keys()
dag=next(iter(bag.dags.values()));assert set(dag.task_ids)=={'prepare','build','quality','publish'}
for parent,child in [('prepare','build'),('build','quality'),('quality','publish')]:assert child in dag.get_task(parent).downstream_task_ids
if starter:
    print('Actual starter DagBag import passed');raise SystemExit(0)
from datetime import datetime, timezone
first=dag.test(logical_date=datetime(2026,1,1,tzinfo=timezone.utc));assert first.state==DagRunState.SUCCESS,first.state
receipt=json.loads((w/'receipt.json').read_text());assert receipt['run_id']==first.run_id
(w/'receipt.json').unlink();(w/'fail-quality').touch()
failed=dag.test(logical_date=datetime(2026,1,2,tzinfo=timezone.utc));assert failed.state==DagRunState.FAILED,failed.state
failed_states={ti.task_id:ti.state for ti in failed.get_task_instances()}
assert failed_states['quality']=='failed',failed_states
assert failed_states['publish']=='upstream_failed',failed_states
assert failed_states['prepare']=='success' and failed_states['build']=='success',failed_states
assert not (w/'receipt.json').exists(),'Failure must block publication'
(w/'fail-quality').unlink()
repaired=dag.test(logical_date=datetime(2026,1,3,tzinfo=timezone.utc));assert repaired.state==DagRunState.SUCCESS,repaired.state
assert json.loads((w/'receipt.json').read_text())['run_id']==repaired.run_id
print('Real Airflow execution: success, intentional failure, repaired replay passed')
print('V2_AIRFLOW_EVIDENCE='+json.dumps({'success_run_id':first.run_id,'quality_failure_run_id':failed.run_id,'repaired_run_id':repaired.run_id,'failed_task_states':failed_states,'receipt_bound_to_repaired_run':True,'logical_dates':'fixed teaching fixture dates; wall duration measured by parent verifier'}))
