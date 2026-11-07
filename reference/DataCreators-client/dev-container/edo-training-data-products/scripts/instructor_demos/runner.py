from __future__ import annotations
import json, os, re, shlex, shutil, subprocess, time
from datetime import datetime,timezone
from pathlib import Path
from .contracts import Blocked, bindings, doctor, expand, files, inside, sha, write_json
from .terminal import Terminal
from .browser import Browser

def utc():return datetime.now(timezone.utc).isoformat()
def assertion(root,workspace,check,observed,values):
    kind=check['kind']
    if kind=='output-contains':
        assert check['text'] in observed['output'], 'Expected diagnostic absent: '+check['text']
        return {'kind':kind,'text':check['text'],'passed':True}
    if kind in ('file-present','file-absent'):
        path=inside(workspace,expand(check['path'],values)); exists=path.is_file()
        assert exists==(kind=='file-present'),kind+': '+str(path)
        return {'kind':kind,'path':check['path'],'passed':True,'sha256':sha(path) if exists else None}
    if kind=='command':
        argv=[expand(x,values) for x in check['argv']]
        p=subprocess.run(argv,cwd=workspace,env={**os.environ,'V2_DB_PATH':str(workspace/'training.duckdb')},capture_output=True,text=True,timeout=120)
        assert p.returncode==check.get('exit_code',0),p.stdout+p.stderr
        assert check.get('contains','') in p.stdout,p.stdout
        return {'kind':kind,'argv':check['argv'],'exit_code':p.returncode,'output':p.stdout.strip(),'passed':True}
    raise ValueError('Unregistered assertion '+kind)

def capture(root,path,story,run_id,dry_run=False):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',run_id):raise ValueError('Unsafe run ID')
    workroot=root/'.local/instructor-demos'/run_id/story['id']
    out=root/'designer/reviews/instructor-demos'/run_id/story['id']
    if workroot.exists() or out.exists():raise ValueError('Capture exists; use a fresh run ID')
    if dry_run:return {'story':story['id'],'requires':story['requires'],'actions':story['steps'],'workspace':str(workroot),'cleanup':story['cleanup']}
    original=bindings(root,path,story)
    readiness=doctor(root,story['requires'])
    result={'schema_version':1,'run_id':run_id,'story':story,'status':'running','route':story['route'],'runtime':readiness,'source_hashes':original,'started_at':utc(),'checkpoints':[],'cleanup':[],'review':None,'recording':'raw real-time browser recording; no compressed waits'}
    out.mkdir(parents=True)
    if story['readiness']=='draft' or any(v['status']=='blocked' for v in readiness.values()):
        result['status']='blocked';result['reason']='Draft requires live rehearsal' if story['readiness']=='draft' else 'Missing declared prerequisites';result['finished_at']=utc();write_json(out/'capture-manifest.json',result);return result
    workroot.mkdir(parents=True);workspace=workroot/'workspace'
    if story.get('workspace_source'):shutil.copytree(inside(root,story['workspace_source']),workspace,ignore=shutil.ignore_patterns('target','logs','__pycache__','*.duckdb*','.venv','.user.yml'))
    else:workspace.mkdir()
    for entry in story.get('workspace_files',[]):
        destination=inside(workspace,entry['destination']);destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists():raise ValueError('Workspace file overwrite refused')
        shutil.copy2(inside(root,entry['source']),destination)
    values={'workspace':str(workspace),'root':str(root),'run_id':run_id,'resource':('demo-'+run_id+'-'+story['id']).lower(),'dbt':os.environ.get('DEMO_DBT_BIN',shutil.which('dbt') or 'dbt'),'dbt_python':os.environ.get('DEMO_DBT_PYTHON','python3'),'python':shutil.which('python3') or 'python3'}
    browser=None;sessions={};start=time.monotonic();interrupted=False
    write_json(out/'resource-ledger.json',{'workspace':str(workspace),'owned':story['resources'],'values':{'resource':values['resource']},'state':'active'})
    write_json(out/'capture-manifest.json',result)
    try:
        browser=Browser(workroot)
        start=time.monotonic()
        for step in story['steps']:
            action={k:expand(v,values) if isinstance(v,str) else v for k,v in step['action'].items()}
            adapter=action['adapter'];timestamp=utc();step_start=time.monotonic()-start
            if adapter=='terminal':
                session=action['session']
                browser.terminal_input(action.get('command',action.get('input','')),step['capture']['context'])
                if session not in sessions:sessions[session]=Terminal(workspace,{**os.environ,'PATH':str(Path(values['dbt']).parent)+':'+os.environ['PATH'],'V2_DB_PATH':str(workspace/'training.duckdb'),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false','DBT_USE_COLORS':'false'},browser.terminal_output)
                observed=sessions[session].run(command=action.get('command'),input_text=action.get('input'),complete=action.get('complete',True),wait_for=action.get('wait_for'),timeout=action.get('timeout_seconds',120),control=action.get('control'))
            else:observed=browser.act(action)
            if 'exit_code' in step['expect']:assert observed['exit_code']==step['expect']['exit_code'],f"{step['id']}: exit {observed['exit_code']} != {step['expect']['exit_code']}"
            evidence=[assertion(root,workspace,c,observed,values) for c in step['expect']['checks']]
            if bindings(root,path,story)!=original:raise ValueError('Source/config drift during capture')
            browser.hold(step['capture'].get('hold_seconds',2))
            frame=workroot/(step['id']+'.png');browser.frame(frame,adapter,step['capture'].get('focus'))
            checkpoint={'story_id':story['id'],'step_id':step['id'],'action_time':timestamp,'observation_time':utc(),'action':step['action'],'executed_action':action,'observation':observed,'assertions':evidence,'context':step['capture']['context'],'caption':step['caption'],'frame':frame.name,'frame_sha256':sha(frame),'dimensions':{'viewport':[1100,600],'device_scale_factor':2},'focus':step['capture'].get('focus'),'time_range':[round(step_start,3),round(time.monotonic()-start,3)]}
            result['checkpoints'].append(checkpoint);write_json(out/'capture-manifest.json',result)
        result['status']='captured'
    except (KeyboardInterrupt,SystemExit) as e:
        result['status']='interrupted';result['reason']=type(e).__name__;interrupted=True
    except Exception as e:
        result['status']='failed';result['reason']=str(e)
        result['failed_step']={'step_id':step['id'] if 'step' in locals() else None,'observation':observed if 'observed' in locals() else None}
    finally:
        for name,terminal in sessions.items():
            (workroot/(name+'.raw.txt')).write_text(terminal.raw)
            write_json(workroot/(name+'.events.json'),terminal.events)
            terminal.close()
        if browser:
            try:result['videos']=[{'path':str(Path(p).relative_to(workroot)),'sha256':sha(p)} for p in browser.close()]
            except Exception as e:result['status']='failed';result['reason']='Video finalization: '+str(e)
        for cleanup in story['cleanup']:
            cmd=expand(cleanup,values)
            try:
                p=subprocess.run(['bash','-c',cmd],cwd=workspace,capture_output=True,text=True,timeout=60)
                result['cleanup'].append({'command':cleanup,'exit_code':p.returncode,'output':(p.stdout+p.stderr).strip()})
                if p.returncode!=0:result['status']='failed';result['reason']='Owned-resource cleanup failed'
            except Exception as e:result['cleanup'].append({'command':cleanup,'error':str(e)});result['status']='failed'
        if bindings(root,path,story)!=original:result['status']='failed';result['reason']='Source/config drift at completion'
        result['duration_seconds']=round(time.monotonic()-start,3);result['finished_at']=utc()
        result['private_artifacts']={'path':str(workroot),'files':files(workroot)}
        write_json(out/'resource-ledger.json',{'workspace':str(workspace),'owned':story['resources'],'cleanup':result['cleanup'],'state':'owned services cleaned; private workspace retained for investigation'})
        write_json(out/'capture-manifest.json',result)
    if interrupted:raise KeyboardInterrupt
    return result


def check_capture(root,path,story,manifest):
    if manifest['status']!='captured':raise ValueError('Only captured stories can be published')
    if manifest['source_hashes']!=bindings(root,path,story):raise ValueError('Stale source/config evidence; capture again')
    if manifest['story']!=story:raise ValueError('Story metadata differs')
    work=Path(manifest['private_artifacts']['path'])
    if files(work)!=manifest['private_artifacts']['files']:raise ValueError('Private capture/workspace bytes changed')
    if len(manifest['checkpoints'])!=len(story['steps']):raise ValueError('Missing checkpoint')
    for step in manifest['checkpoints']:
        if sha(work/step['frame'])!=step['frame_sha256']:raise ValueError('Frame checksum mismatch')
    return True
