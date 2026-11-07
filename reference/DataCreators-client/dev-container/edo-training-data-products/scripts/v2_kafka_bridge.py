#!/usr/bin/env python3
"""Training broker bridge with explicit event/run/output identity and bounded waits."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def validate_event(e):
 from datetime import datetime
 if not isinstance(e,dict) or not {'event_id','type','dataset_id','dataset_version','location','arrived_at'}<=e.keys():raise ValueError('Missing event fields')
 if e['type']!='dataset_arrived' or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',e['event_id']):raise ValueError('Invalid event type/identity')
 if (e['dataset_id'],e['dataset_version'],e['location'])!=('holdings','fixture-v1','fixture://holdings-v1'):raise ValueError('Unknown dataset fixture')
 if datetime.fromisoformat(e['arrived_at'].replace('Z','+00:00')).tzinfo is None:raise ValueError('Arrival timestamp needs timezone')
 return e

def run_id(e):return 'v2_event_'+hashlib.sha256(e['event_id'].encode()).hexdigest()[:32]

def trigger(e,a):
 rid=run_id(e)
 out=subprocess.check_output([a.airflow,'dags','list-runs',a.dag_id,'--output','json'],text=True)
 existing=json.loads(next((line for line in reversed(out.splitlines()) if line[:1] in '[{'),'[]'))
 if any(r.get('run_id')==rid for r in existing):raise ValueError('Existing run without matching completed receipt: offset uncommitted; inspect that exact run')
 subprocess.run([a.airflow,'dags','trigger',a.dag_id,'--run-id',rid,'--conf',json.dumps({'event':e})],check=True)
 return rid

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('action',choices=['validate','prepare-topic','produce','consume','verify-chain']);ap.add_argument('--event',type=Path);ap.add_argument('--bootstrap',default='localhost:19092');ap.add_argument('--topic',default='v2-dataset-arrived');ap.add_argument('--group',default='v2-training');ap.add_argument('--airflow',default='airflow');ap.add_argument('--dag-id',default='v2_training_pipeline');ap.add_argument('--receipt',type=Path);ap.add_argument('--project',type=Path);ap.add_argument('--evidence',type=Path,default=Path('event-evidence.json'));ap.add_argument('--timeout',type=float,default=30)
 a=ap.parse_args();e=validate_event(json.loads(a.event.read_text())) if a.event else None
 if a.action in ['validate','produce','verify-chain'] and e is None:ap.error('--event required')
 if a.action=='validate':print(json.dumps({'valid':True,'run_id':run_id(e)}));return
 if a.action=='verify-chain':
  if not a.receipt or not a.project:ap.error('--receipt and --project required')
  receipt=json.loads(a.receipt.read_text());evidence=json.loads(a.evidence.read_text())
  assert receipt['event']==e and receipt['run_id']==run_id(e)
  assert evidence['event']==e and evidence['run_id']==run_id(e) and isinstance(evidence['partition'],int) and isinstance(evidence['offset'],int)
  import importlib.util
  spec=importlib.util.spec_from_file_location('v2',Path(__file__).with_name('challenge-v2.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.exposure(a.project.resolve())
  print('Broker event/run/receipt/dbt output chain verified');return
 from confluent_kafka import Producer,Consumer
 if a.action=='prepare-topic':
  from confluent_kafka.admin import AdminClient,NewTopic
  client=AdminClient({'bootstrap.servers':a.bootstrap});metadata=client.list_topics(timeout=a.timeout)
  if a.topic not in metadata.topics:client.create_topics([NewTopic(a.topic,1,1)])[a.topic].result(timeout=a.timeout)
  assert not client.list_topics(a.topic,timeout=a.timeout).topics[a.topic].error
  print('Topic ready: '+a.topic);return
 if a.action=='produce':
  p=Producer({'bootstrap.servers':a.bootstrap});results=[]
  def delivery(err,msg):results.append({'error':str(err)} if err else {'partition':msg.partition(),'offset':msg.offset()})
  p.produce(a.topic,key=e['event_id'],value=json.dumps(e),on_delivery=delivery)
  assert p.flush(a.timeout)==0 and results and 'error' not in results[0],results
  print(json.dumps({'broker':results[0],'downstream':'pending'}));return
 c=Consumer({'bootstrap.servers':a.bootstrap,'group.id':a.group,'auto.offset.reset':'earliest','enable.auto.commit':False});c.subscribe([a.topic])
 try:
  msg=c.poll(a.timeout)
  if msg is None:raise TimeoutError('No event in bounded wait')
  if msg.error():raise RuntimeError(msg.error())
  e=validate_event(json.loads(msg.value()));rid=run_id(e);decision='new run'
  previous=json.loads(a.receipt.read_text()) if a.receipt and a.receipt.exists() else None
  if previous and previous['run_id']==rid:
   if previous['event']!=e:raise ValueError('Conflicting payload with the same identity; offset uncommitted')
   decision='identical completed run reused'
  else:rid=trigger(e,a)
  record={'event':e,'run_id':rid,'partition':msg.partition(),'offset':msg.offset(),'topic':a.topic,'decision':decision,'downstream':'pending'}
  a.evidence.write_text(json.dumps(record,indent=2)+'\n');c.commit(message=msg,asynchronous=False);print(json.dumps(record,indent=2))
 finally:c.close()
if __name__=='__main__':main()
