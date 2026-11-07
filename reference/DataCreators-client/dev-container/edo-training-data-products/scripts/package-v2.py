#!/usr/bin/env python3
"""Deterministic separate learner/instructor archives with content-level answer checks."""
import argparse,fnmatch,hashlib,importlib.util,json,os,re,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IGNORED={'.local','.git','.venv','node_modules','__pycache__','target','logs','dbt_packages','.pytest_cache','.databricks'}
AUTHORING_PATHS={('challenges','courseware'),('.devcontainer','authoring')}
SECRETS=['*.duckdb*','*.wal','*.db','*.pyc','*.env','.env','.env.*','*.pem','*.key','.databrickscfg','airflow_settings.yaml','simple_auth_manager_passwords*']
INSTRUCTOR_DIRS={'solution','solutions','v2-solutions','instructor-demos','instructor_demos'}
INSTRUCTOR_FILES={'instructor-demos.py','demo-checks.py','devc-smoke.py','setup-instructor-demos.sh','run-devc-audit.py','separate-v2-stretch-answers.py','challenge-run-brief.md','package-v2.py','package-v2.sh','sync-v2-course.py','build-v2-course.sh','review-v2-course.py','v2-presentation.lua'}
def sha(data):return hashlib.sha256(data).hexdigest()

def inventory():
    paths=[]
    for folder,dirs,names in os.walk(ROOT):
        dirs[:]=sorted(n for n in dirs if n not in IGNORED and not (Path(folder)==ROOT and n=='designer') and (Path(folder)/n).relative_to(ROOT).parts[:2] not in AUTHORING_PATHS)
        for name in sorted(names):
            if name!='.env.example' and any(fnmatch.fnmatch(name,p) for p in SECRETS):continue
            p=Path(folder)/name
            if p.is_symlink():raise ValueError('Package symlink requires explicit classification: '+str(p))
            paths.append(p)
    return paths

def build(output):
    output.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('separation',ROOT/'scripts/separate-v2-stretch-answers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    sources=inventory();record={}
    for kind in ['learner','instructor']:
        contents={};transforms=[]
        for p in sources:
            rel=p.relative_to(ROOT);parts=set(rel.parts)
            if kind=='learner' and (parts&INSTRUCTOR_DIRS or p.name in INSTRUCTOR_FILES or rel.parts[:2] in [('tests','challenges'),('docs','superpowers')]):continue
            data=p.read_bytes()
            if kind=='learner' and p.suffix=='.md':
                text=data.decode();stripped,answers=module.transform(text,'legacy')
                if answers:
                    stripped=re.sub(r'`challenges/v2-solutions/legacy/phase-two-proficient/legacy-stretch-answers.md`','the separately supplied instructor archive',stripped)
                    data=stripped.encode();transforms.append({'path':str(rel),'source_sha256':sha(p.read_bytes()),'learner_sha256':sha(data),'answer_blocks_excluded':len(answers),'instructor_source_retained':True})
                if re.search(r'<summary>.*(?:[Ss]olution|[Aa]nswer)',data.decode()):raise ValueError('Unclassified embedded learner answer: '+str(rel))
            contents[str(rel)]=data
        if kind=='instructor':
            for p in sorted((ROOT/'designer').glob('*.md')):
                contents[str(p.relative_to(ROOT))]=p.read_bytes()
        manifest=json.loads(contents['challenges/v2/manifest.json'])
        inventory_path=manifest['source_inventory']
        if Path(inventory_path).is_absolute() or '..' in Path(inventory_path).parts:raise ValueError('Unsafe manifest inventory path')
        # Deliver a truthful inventory of the selected archive bytes, rather
        # than omitting the manifest's referenced authoring-only baseline file.
        contents[inventory_path]=(json.dumps({'source_revision':manifest['source_revision'],'scope':'Packaged candidate bytes; historical upstream revision retained; current files hashed below','files':{n:sha(data) for n,data in sorted(contents.items()) if n!=inventory_path},'answer_transforms':transforms},indent=2)+'\n').encode()
        name=f'DataCreators-challenges-v2-{kind}.zip';path=output/name
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in sorted(contents.items()):
                info=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0));info.external_attr=(0o100755 if os.access(ROOT/name,os.X_OK) else 0o100644)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
        with zipfile.ZipFile(path) as z:
            actual={i.filename:sha(z.read(i)) for i in z.infolist()}
        assert actual=={n:sha(data) for n,data in contents.items()},'Archive readback differs'
        record[kind]={'archive':path.name,'sha256':sha(path.read_bytes()),'files':actual,'presentation_transforms':transforms,'source_root':str(ROOT),'solution_separation':'Full answer files and instructor capture system excluded from learner archive; recognized legacy embedded solutions omitted only during packaging, originals retained in instructor archive'}
    (output/'package-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    return record

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'designer/dist');a=ap.parse_args();record=build(a.output.resolve())
    print(json.dumps({kind:{k:v for k,v in data.items() if k in ['archive','sha256']} for kind,data in record.items()},indent=2))
if __name__=='__main__':main()
