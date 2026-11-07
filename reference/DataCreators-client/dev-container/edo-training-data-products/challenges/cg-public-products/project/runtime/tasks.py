"""Supplied worker task I/O and publication boundary, not assessed transformation logic.

All writes use the approved catalog/schema and an owned relation prefix. dbt builds
candidate relations; acceptance changes a view only after quality succeeds. Receipts
can lag a committed pointer update: replay is required to finish that checkpoint.
"""
import hashlib
import json
import os
import re
import subprocess
import shutil
import tempfile
import fcntl
from pathlib import Path
from runtime.io_support import digest,atomic_json,ensure_generated_seed,write_history
from runtime.product import ROOT,STAGED_MANIFEST,code_manifest,owned_prefix


def validate_config(config):
    required={'dag_id','relation_prefix','batch_id','connection_id','phase'}
    if not required<=set(config):raise ValueError('Missing blueprint configuration field')
    if not re.fullmatch('[a-z][a-z0-9_]{2,55}',config['relation_prefix']):
        raise ValueError('Set a valid unique owned relation_prefix; no placeholders')
    if 'replace_me' in config['relation_prefix'].lower():raise ValueError('Replace the namespace placeholder')
    if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_-]{2,99}',config['dag_id']):raise ValueError('Invalid dag_id')
    if config['phase'] not in [1,2,3]:raise ValueError('phase must be 1, 2 or 3')
    if not isinstance(config['batch_id'],str) or not config['batch_id']:raise ValueError('Missing batch_id')
    if not isinstance(config['connection_id'],str) or not config['connection_id']:raise ValueError('Missing connection_id')
    return dict(config)


def project():
    return ROOT


def dbt_executable(env):
    # The shared Astro image keeps dbt-databricks in its separate Cosmos venv.
    worker_dbt=Path('/home/astro/.venv/cosmos/bin/dbt')
    return env.get('CG_DBT_EXECUTABLE') or (str(worker_dbt) if worker_dbt.is_file() else 'dbt')


def worker_environment(config):
    # Resolve a fresh credential inside the worker; a laptop OAuth session is not enough.
    from airflow.sdk import BaseHook
    conn=BaseHook.get_connection(config['connection_id'])
    extra=conn.extra_dejson
    env=dict(os.environ)
    env['DATABRICKS_HOST']=conn.host
    env['DATABRICKS_HTTP_PATH']=extra.get('http_path') or env.get('DATABRICKS_HTTP_PATH','')
    env['DBT_ACCESS_TOKEN']=conn.password or extra.get('token','')
    if not env['DBT_ACCESS_TOKEN'] or not env['DATABRICKS_HTTP_PATH']:
        raise RuntimeError('Worker connection needs fresh token and SQL warehouse http_path')
    # Candidate identity depends on input and executable version, not the DAG attempt.
    manifest_bytes=(project()/'data/manifest.json').read_bytes()
    input_manifest=json.loads(manifest_bytes)
    for name,record in input_manifest['files'].items():
        path=project()/'data'/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('Staged input differs from its manifest: '+name)
    source_hash=hashlib.sha256(manifest_bytes).hexdigest()
    owned_prefix(config['relation_prefix'])
    if not STAGED_MANIFEST.is_file():raise RuntimeError('Run runtime/stage_astro.py before triggering this product')
    if json.loads(STAGED_MANIFEST.read_text())!=code_manifest():
        raise RuntimeError('Product code changed after staging; finish active runs, then rerun runtime/stage_astro.py')
    code_hash=hashlib.sha256(STAGED_MANIFEST.read_bytes()).hexdigest()
    config=dict(config,input_manifest_sha256=source_hash,staged_code_sha256=code_hash)
    candidate=digest({'batch_id':config['batch_id'],'phase':config['phase'],'input':source_hash,'code':code_hash})[:10]
    env['DC_RELATION_PREFIX']=config['relation_prefix']+'_candidate_'+candidate
    for key in ['DBT_CATALOG','DBT_SCHEMA','DATABRICKS_HOST']:
        if not env.get(key):raise RuntimeError('Missing worker setting '+key)
    return config,env


def run_root(config):
    # Each namespace/batch/code/input combination gets its own writable project.
    # Two blueprint instances must not race on generated seeds, target files or ledgers.
    key=digest({'prefix':config['relation_prefix'],'batch':config['batch_id'],'phase':config['phase'],
                'code':config['staged_code_sha256'],'input':config['input_manifest_sha256']})[:24]
    parent=project()/'.local/work';parent.mkdir(parents=True,exist_ok=True)
    destination=parent/key
    if not destination.exists():
        temporary=Path(tempfile.mkdtemp(prefix='prepare-',dir=parent))
        try:
            for name in ['models','macros','tests','data','runtime']:
                shutil.copytree(project()/name,temporary/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            for name in ['dbt_project.yml','profiles.yml']:
                shutil.copy2(project()/name,temporary/name)
            shutil.copy2(STAGED_MANIFEST,temporary/'staged-code-manifest.json')
            ensure_generated_seed(temporary)
            try:temporary.rename(destination)
            except OSError:
                if not destination.exists():raise
        finally:
            if temporary.exists():shutil.rmtree(temporary)
    return destination


def dbt(config,arguments):
    config,env=worker_environment(validate_config(config))
    flags={'enable_phase_1':True,'enable_phase_2':config['phase']>=2,'enable_phase_3':config['phase']>=3}
    root=run_root(config)
    command=[dbt_executable(env),*arguments,'--project-dir',str(root),'--profiles-dir',str(root),'--target','training','--vars',json.dumps(flags)]
    # No shell interpolation or token logging. dbt retains detailed operational logs locally.
    result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=240)
    if result.returncode:
        raise RuntimeError('dbt command failed; inspect worker/project dbt logs and failed node')
    return config,env


def load(config):
    config=validate_config(config)
    config,env=worker_environment(config)
    root=run_root(config)
    ensure_generated_seed(root)
    if config['phase']==3:
        from runtime.temporal_loader import apply_event
        # Persist the synthetic ledger/history for semantic replay, separate from attempt logs.
        # Accepted history/ledger belong to the namespace, not to a single batch/code version.
        # That keeps earlier knowledge when a later delivery arrives in another run workspace.
        state_dir=project()/'.local/temporal';state_dir.mkdir(parents=True,exist_ok=True)
        state_path=state_dir/(config['relation_prefix']+'.json')
        with state_path.with_suffix('.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            state=json.loads(state_path.read_text()) if state_path.exists() else {'history':[],'ledger':{}}
            history,ledger=state['history'],state['ledger']
            for event in json.loads((root/'data/training_events.json').read_text()):
                history,ledger=apply_event(history,ledger,event)
            # The generated seed is instance/run scoped; state writes are atomic under the lock.
            write_history(root,history)
            atomic_json(state_path,{'history':history,'ledger':ledger})
    dbt(config,['seed'])


def build(config):
    select='tag:phase1' if config['phase']==1 else 'tag:phase1 tag:phase2'+(' tag:phase3' if config['phase']==3 else '')
    dbt(config,['run','--select',select])


def quality(config):
    select='tag:phase1' if config['phase']==1 else 'tag:phase1 tag:phase2'+(' tag:phase3' if config['phase']==3 else '')
    dbt(config,['test','--select',select])


def execute_sql(env, statements):
    # Execute using the dbt environment, rather than assuming its adapter is in Airflow's venv.
    executable=Path(dbt_executable(env))
    python_path=str(executable.parent/'python') if executable.is_absolute() else 'python'
    result=subprocess.run([python_path,str(project()/'runtime/sql_client.py')],
                          input=json.dumps(statements),env=env,capture_output=True,text=True,timeout=180)
    if result.returncode:raise RuntimeError('Owned warehouse statement failed; inspect protected runtime logs')
    return json.loads(result.stdout)


def quote_identifier(value):
    if not re.fullmatch('[A-Za-z_][A-Za-z0-9_-]{0,254}',value):raise ValueError('Invalid SQL identifier')
    return '`'+value+'`'


def receipt(config):
    from airflow.sdk import get_current_context
    context=get_current_context();config,env=worker_environment(validate_config(config))
    model='dom_cg__product_cost' if config['phase']==1 else 'rpt_cg__product_research'
    candidate=env['DC_RELATION_PREFIX']+'_'+model
    accepted=config['relation_prefix']+'_accepted_product_research'
    namespace='.'.join(quote_identifier(env[k]) for k in ['DBT_CATALOG','DBT_SCHEMA'])
    identity=digest({'prefix':config['relation_prefix'],'batch':config['batch_id'],'phase':config['phase'],'input':config['input_manifest_sha256'],'code':config['staged_code_sha256']})
    path=project()/'evidence/runtime/releases'/(identity+'.json')
    if path.exists():return json.loads(path.read_text())
    count=execute_sql(env,[{'sql':'select count(*) from '+namespace+'.'+quote_identifier(candidate),'fetch':True}])[0][0][0]
    if count!=(25 if config['phase']==1 else 109):raise ValueError('Release population does not match scope')
    # Gate already succeeded: atomically switch the accepted view, then acknowledge it.
    execute_sql(env,[{'sql':'create or replace view '+namespace+'.'+quote_identifier(accepted)+' as select * from '+namespace+'.'+quote_identifier(candidate)}])
    value={'release_id':identity,'batch_id':config['batch_id'],'candidate':candidate,'accepted_view':accepted,
           'row_count':count,'quality_result':'passed','dag_run_id':context['run_id'],
           'input_manifest_sha256':config['input_manifest_sha256'],'staged_code_sha256':config['staged_code_sha256']}
    atomic_json(path,value)
    return value


def smoke(nonce,prefix,connection_id):
    # Supplied neutral worker check; a fresh nonce prevents accepting an old receipt.
    if not re.fullmatch('[a-f0-9]{16,40}',nonce):raise ValueError('Invalid smoke nonce')
    cfg=dict(dag_id='cg_environment_smoke',relation_prefix=prefix,batch_id='smoke-'+nonce,phase=1,connection_id=connection_id)
    cfg,env=worker_environment(validate_config(cfg));root=run_root(cfg);ensure_generated_seed(root)
    flags={'run_nonce':nonce,'enable_phase_1':False,'enable_phase_2':False,'enable_phase_3':False}
    cmd=[dbt_executable(env),'build','--select','+cg_environment_smoke','--project-dir',str(root),'--profiles-dir',str(root),'--target','training','--vars',json.dumps(flags)]
    result=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,timeout=240)
    if result.returncode:raise RuntimeError('Worker smoke dbt build failed; inspect runtime logs')
    relation='.'.join(quote_identifier(env[k]) for k in ['DBT_CATALOG','DBT_SCHEMA'])+'.'+quote_identifier(env['DC_RELATION_PREFIX']+'_cg_environment_smoke')
    rows=execute_sql(env,[{'sql':'select seed_rows,seed_sum,run_nonce from '+relation,'fetch':True}])[0]
    if len(rows)!=1 or list(rows[0])!=[2,3,nonce]:raise ValueError('Wrong neutral warehouse smoke result')
    from airflow.sdk import get_current_context
    receipt={'nonce':nonce,'seed_rows':2,'seed_sum':3,'dag_run_id':get_current_context()['run_id'],
             'relation':relation,'staged_code_sha256':cfg['staged_code_sha256'],'worker_execution':True}
    atomic_json(project()/'evidence/runtime/smoke'/(nonce+'.json'),receipt)
    return receipt
