#!/usr/bin/env python3
"""Read current Airflow 3 API evidence; no scheduling, mutation or production publication."""
import argparse, hashlib, json, os, sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
BASE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',type=Path);p.add_argument('--success',required=True);p.add_argument('--failure',required=True);p.add_argument('--repair',required=True);p.add_argument('--after',required=True,help='ISO8601 session start; runs must be newer');a=p.parse_args()
 url=os.environ.get('DC_AIRFLOW_API_URL');token=os.environ.get('DC_AIRFLOW_API_TOKEN')
 if not url or not token:print('PENDING: prepared Astro API URL/token unavailable',file=sys.stderr);sys.exit(77)
 from datetime import datetime
 after=datetime.fromisoformat(a.after.replace('Z','+00:00'));assert after.tzinfo
 owner=json.loads((a.stage/'ownership.json').read_text());dag=owner['prefix']+'_portfolio_daily';report={'dag_id':dag,'runs':{},'session_started_at':a.after,'contract_sha256':hashlib.sha256((BASE/'dataset-runtime-contract.json').read_bytes()).hexdigest(),'boundary':'current scheduled Astro API identities and checked worker receipts; human UI/auth restart separate'}
 def get(path):
  req=Request(url.rstrip('/')+'/api/v2/'+path,headers={'Authorization':'Bearer '+token})
  with urlopen(req,timeout=30) as r:return json.load(r)
 assert len({a.success,a.failure,a.repair})==3,'Use three distinct fresh runs'
 from urllib.parse import unquote
 if os.environ.get('DEMO_AIRFLOW_RUN_URL'):
  url_text=unquote(os.environ['DEMO_AIRFLOW_RUN_URL']);assert any(rid in url_text for rid in [a.success,a.repair]),'UI run URL must bind this verified success/repair identity'
 if os.environ.get('DEMO_AIRFLOW_LOG_URL'):
  assert a.failure in unquote(os.environ['DEMO_AIRFLOW_LOG_URL']),'UI log URL must bind the verified failed run'

 for label,rid in [('success',a.success),('failure',a.failure),('repair',a.repair)]:
  path='dags/'+quote(dag,safe='')+'/dagRuns/'+quote(rid,safe='');run=get(path);tasks=get(path+'/taskInstances')['task_instances'];states={t['task_id']:t['state'] for t in tasks}
  assert run['dag_id']==dag and run['dag_run_id']==rid,'Run identity drift'
  assert run.get('run_type')=='scheduled','Only scheduler-created run establishes the assigned timetable'
  started=datetime.fromisoformat(run['start_date'].replace('Z','+00:00'));assert started>after,'Historical run cannot supply current evidence'
  receipt=a.stage/'evidence'/(rid.replace(':','_').replace('/','_')+'.json')
  if label=='failure':
   assert run['state']=='failed' and states.get('quality')=='failed' and states.get('publication_evidence')=='upstream_failed',states
   assert not receipt.exists(),'Failed run must not create publication evidence'
  else:
   assert run['state']=='success' and set(states)=={'source_ready','dbt_build','quality','publication_evidence'} and set(states.values())=={'success'},states
   r=json.loads(receipt.read_text());assert r['run_id']==rid and r['contract_sha256']==report['contract_sha256']
   assert r['config']['DC_RELATION_PREFIX']==owner['prefix'] and r['rows_checked']==8
   assert r['partition'] in {'2026-05-20','2026-05-21'} and len(r['partition_rows'])==4
   assert all(row[1]==r['partition'] for row in r['partition_rows']),'Receipt contains another business date'
  report['runs'][label]={'run':run,'task_states':states,'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest() if receipt.exists() else None}
 import importlib.util
 spec=importlib.util.spec_from_file_location('scheduled_portfolio_lab',BASE/'lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
 report['independent_warehouse_check']=lab.check(a.stage/'project','portfolio')
 (a.stage/'scheduled-evidence.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: fresh scheduled success, blocked-quality failure and repair identities plus independent warehouse output; inspect log/UI and replay separately')
if __name__=='__main__':main()
