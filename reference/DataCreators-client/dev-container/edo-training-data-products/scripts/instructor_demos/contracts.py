from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess
from pathlib import Path
import jsonschema, yaml

class Blocked(RuntimeError): pass

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(value,indent=2)+'\n'); tmp.replace(path)

def inside(root, relative):
    path=(root/relative).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('Path escapes declared root: '+str(relative))
    return path

def files(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and not {'target','logs','__pycache__','.git','.venv'}.intersection(p.relative_to(root).parts) and not p.name.endswith(('.duckdb','.wal'))}

def load_story(root,path):
    story=yaml.safe_load(path.read_text())
    schema=json.loads((root/'instructor-demos/schema/story.schema.json').read_text())
    jsonschema.Draft202012Validator(schema).validate(story)
    if path.parent.name!=story['id']: raise ValueError('Story directory and ID differ')
    ids=[s['id'] for s in story['steps']]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate step IDs')
    manifest=json.loads((root/'challenges/v2/manifest.json').read_text())
    known={x['id'] for t in manifest['tools'] for p in t['phases'] for x in p['tasks']} | set(manifest.get('assigned_guide_task_ids', []))
    if not set(story['task_ids'])<=known: raise ValueError('Unknown current challenge task ID')
    for source in story['source_inputs']:
        if not inside(root,source).exists(): raise ValueError('Missing source input: '+source)
    if story.get('workspace_source'):
        if not inside(root,story['workspace_source']).is_dir(): raise ValueError('Missing workspace source')
    for entry in story.get('workspace_files',[]):
        if entry['source'] not in story['source_inputs']:raise ValueError('Workspace file must be source-bound')
        inside(root,entry['source'])
        inside(Path('/workspace'),entry['destination'])
    return story

def bindings(root,path,story):
    result={'story.yaml':sha(path),'manifest.json':sha(root/'challenges/v2/manifest.json')}
    for rel in sorted(set(story['source_inputs']+[story['workspace_source']] if story.get('workspace_source') else story['source_inputs'])):
        p=inside(root,rel)
        if p.is_dir(): result.update({rel+'/'+k:v for k,v in files(p).items()})
        else: result[rel]=sha(p)
    # Shared executable code/theme/schema are part of evidence freshness.
    for directory in ['scripts/instructor_demos','instructor-demos/schema','instructor-demos/theme']:
        result.update({directory+'/'+k:v for k,v in files(root/directory).items()})
    for rel in ['scripts/demo-checks.py','scripts/instructor-demos.py','instructor-demos/requirements.lock']:
        result[rel]=sha(root/rel)
    return result

def doctor(root,requirements):
    results={}
    for requirement in requirements:
        status='available'; details=''
        if requirement.startswith('env:'):
            key=requirement[4:]; value=os.environ.get(key)
            if not value: status='blocked';details='Set instructor-assigned '+key+' outside recording'
            else: details='configured; value withheld'
        elif requirement=='browser':
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    b=p.chromium.launch();details=b.version;b.close()
            except Exception as e: status='blocked'; details=str(e).splitlines()[0]
        else:
            name={'docker-server':'docker','docker-client':'docker','dbt':'dbt','duckdb-python':'python'}.get(requirement,requirement)
            override={'dbt':'DEMO_DBT_BIN','duckdb-python':'DEMO_DBT_PYTHON'}.get(requirement)
            exe=os.environ.get(override,'') if override else ''
            exe=exe or shutil.which(name)
            if not exe: status='blocked';details=name+' executable unavailable'
            else:
                cmd=[exe,'info','--format','{{.ServerVersion}}'] if requirement=='docker-server' else [exe,'-c','import duckdb;print(duckdb.__version__)'] if requirement=='duckdb-python' else [exe,'--version']
                try:
                    p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
                    status='available' if p.returncode==0 else 'blocked'
                    details=(p.stdout or p.stderr).strip()[:1500]
                except (OSError,subprocess.TimeoutExpired) as e: status='blocked';details=str(e)
        results[requirement]={'status':status,'detail':details}
    return results

# Only explicit template names are substituted; shell/Jinja braces remain literal.
def expand(text,values):
    def replace(match):
        key=match[1]
        if key.startswith('env.'):
            value=os.environ.get(key[4:])
            if value is None: raise Blocked('Missing environment assignment '+key[4:])
            return value
        if key not in values: raise ValueError('Unknown template '+key)
        return str(values[key])
    return re.sub(r'\{\{([a-zA-Z_][\w.]*)\}\}',replace,text)
