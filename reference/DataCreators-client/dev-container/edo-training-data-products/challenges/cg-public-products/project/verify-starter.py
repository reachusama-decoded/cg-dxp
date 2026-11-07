#!/usr/bin/env python3
"""Public environment verification. This never certifies a capstone solution.

files: portable syntax/input/smoke checks, no installed training tools needed.
local: files plus Docker/CLI readiness, dbt smoke compile and shared Astro import check.
connected: local plus warehouse smoke and an actual scheduler/worker DAG run.
Missing tools/evidence are explicit; a stale receipt or DAG import is not success.
"""
import argparse
import ast
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from runtime.io_support import ensure_generated_seed,atomic_json
CHECKS=[]


def record(name,status,detail):
    CHECKS.append({'check':name,'status':status,'detail':detail})


def command(name,args,cwd=ROOT,timeout=120,required=True):
    # Retain no raw stdout/stderr: CLI auth/debug output can expose environment details.
    try:
        result=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout)
        record(name,'pass' if result.returncode==0 else 'fail',{'exit_code':result.returncode})
        return result
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        record(name,'not_run',{'reason':type(exc).__name__})
        return None


def files():
    missing=[p for p in ['dbt_project.yml','profiles.yml','data/manifest.json','models/smoke/cg_environment_smoke.sql','dags/cg_environment_smoke.py','.airflowignore'] if not (ROOT/p).exists()]
    record('starter_files','fail' if missing else 'pass',{'missing':missing})
    for p in ROOT.rglob('*.py'):
        if any(x in p.parts for x in ['.git','.local','__pycache__']):continue
        try:ast.parse(p.read_text())
        except SyntaxError as exc:record('python_syntax','fail',{'file':str(p.relative_to(ROOT)),'line':exc.lineno});break
    else:record('python_syntax','pass',{'meaning':'Parse only; does not import Airflow or run callbacks'})
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    changed=[]
    for name,info in manifest['files'].items():
        p=ROOT/'data'/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=info['sha256']:changed.append(name)
    record('frozen_input_hashes','fail' if changed else 'pass',{'changed':changed})
    rows=list(csv.DictReader((ROOT/'data/cg_smoke.csv').open()))
    record('neutral_smoke_seed','pass' if len(rows)==2 and sum(int(r['value']) for r in rows)==3 else 'fail',{'rows':len(rows),'meaning':'Independent neutral fixture, not CG task output'})
    ensure_generated_seed(ROOT)
    try:
        sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except subprocess.CalledProcessError:sha=None
    return sha


def decode_json(stdout):
    # Astro can put informational text before the Airflow CLI JSON document.
    decoder=json.JSONDecoder()
    for i,c in enumerate(stdout):
        if c in '[{':
            try:
                obj,_=decoder.raw_decode(stdout[i:])
                if isinstance(obj,list):return obj
            except json.JSONDecodeError:pass
    raise ValueError('No CLI JSON list found; check pinned Airflow CLI output syntax')


def local():
    from runtime.workspace import check_workspace
    try:
        details=check_workspace(ROOT)
        record('working_product_and_target', 'pass', details)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        record('working_product_and_target', 'fail', {'reason': str(exc)})
        return
    for name,args in [('docker',['docker','version']),('mise',['mise','--version']),('astro',['astro','version']),('dbt',['dbt','--version']),('databricks',['databricks','--version'])]:
        command('tool_'+name,args)
    missing=[k for k in ['DATABRICKS_HOST','DATABRICKS_HTTP_PATH','DBT_CATALOG','DBT_SCHEMA','DC_RELATION_PREFIX','DBT_ACCESS_TOKEN'] if not os.environ.get(k)]
    record('profile_environment','fail' if missing else 'pass',{'missing_names':missing})
    if missing:return
    if shutil.which('dbt'):
        command('dbt_smoke_compile',['dbt','compile','--select','+cg_environment_smoke','--project-dir',str(ROOT),'--profiles-dir',str(ROOT),'--vars',json.dumps({'run_nonce':'compile_only'})])
    if shutil.which('astro'):
        from runtime.stage_astro import stage
        stage(ROOT)
        # The shared stack parses every product; only this product's import errors count here.
        result=command('astro_import_errors',['astro','dev','run','dags','list-import-errors','--output','json'],cwd=details['client_root'],timeout=240)
        if result and not result.returncode:
            try:
                errors=[e for e in decode_json(result.stdout) if '/'+ROOT.name+'/' in str(e.get('filepath',e.get('bundle_name','')))]
                record('product_import_errors','fail' if errors else 'pass',{'files':[e.get('filepath') for e in errors]})
            except ValueError:
                record('product_import_errors','not_run',{'reason':'Unrecognized Airflow CLI output'})


def connected(timeout):
    if not all(x['status']=='pass' for x in CHECKS):
        record('connected_execution','not_run',{'reason':'Requested local prerequisite checks did not pass'});return
    nonce=uuid.uuid4().hex
    prefix=os.environ['DC_RELATION_PREFIX']
    # Host connection/build proof is separate from worker execution proof.
    command('host_dbt_debug',[sys.executable,str(ROOT/'runtime/dbt_command.py'),'debug'])
    command('host_smoke_build',[sys.executable,str(ROOT/'runtime/dbt_command.py'),'build','--select','+cg_environment_smoke','--vars',json.dumps({'run_nonce':nonce})],timeout=240)
    if any(x['status']!='pass' for x in CHECKS):return
    from runtime.product import dag_id
    cwd=next(x['detail']['client_root'] for x in CHECKS if x['check']=='working_product_and_target')
    dag=dag_id('environment_smoke');run_id='cg_smoke_'+nonce
    command('smoke_unpause',['astro','dev','run','dags','unpause',dag],cwd=cwd)
    trigger=command('smoke_trigger',['astro','dev','run','dags','trigger',dag,'--run-id',run_id,'--conf',json.dumps({'nonce':nonce,'relation_prefix':prefix,'connection_id':'databricks_default'})],cwd=cwd)
    if not trigger or trigger.returncode:return
    deadline=time.monotonic()+timeout;state=None
    while time.monotonic()<deadline:
        # Do not count every polling command as a new assessment check.
        result=subprocess.run(['astro','dev','run','dags','list-runs',dag,'--output','json'],cwd=cwd,capture_output=True,text=True,timeout=45)
        try:
            states=decode_json(result.stdout)
            matching=[r for r in states if r.get('run_id',r.get('dag_run_id'))==run_id]
            state=matching[0].get('state') if matching else None
        except ValueError:state=None
        if state in ['success','failed']:break
        time.sleep(2)
    record('scheduler_worker_run','pass' if state=='success' else 'not_run' if state is None else 'fail',{'run_id':run_id,'state':state})
    receipt=ROOT/'evidence/runtime/smoke'/(nonce+'.json')
    if not receipt.exists():
        record('worker_smoke_receipt','not_run',{'reason':'No worker-visible receipt; verify artifact mounts'});return
    value=json.loads(receipt.read_text())
    valid=value.get('nonce')==nonce and value.get('dag_run_id')==run_id and value.get('seed_rows')==2 and value.get('seed_sum')==3 and value.get('worker_execution') is True
    record('worker_smoke_receipt','pass' if valid else 'fail',{'receipt':str(receipt.relative_to(ROOT)),'nonce':nonce,'run_id':run_id})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['files','local','connected'],default='local')
    parser.add_argument('--output',default='evidence/starter-check.json')
    parser.add_argument('--timeout',type=int,default=300)
    args=parser.parse_args()
    code_sha=files()
    if args.mode in ['local','connected']:local()
    if args.mode=='connected':connected(args.timeout)
    else:record('connected_execution','not_run',{'reason':'Not requested','counts_toward_requested_mode':False})
    mandatory=[c for c in CHECKS if c.get('detail',{}).get('counts_toward_requested_mode') is not False]
    passed=all(c['status']=='pass' for c in mandatory)
    report={'purpose':'Environment readiness only','mode':args.mode,'requested_mode_passed':passed,'connected_verified':args.mode=='connected' and passed,'code_commit_sha':code_sha,'checks':CHECKS}
    atomic_json(ROOT/args.output,report)
    print(json.dumps(report,indent=2))
    return 0 if passed else 1 if any(c['status']=='fail' for c in mandatory) else 2


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError) as exc:
        print('Starter checker error: '+type(exc).__name__,file=sys.stderr)
        raise SystemExit(2)
