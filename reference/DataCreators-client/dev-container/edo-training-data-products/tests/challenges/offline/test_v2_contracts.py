"""Behavioral guards for v2 isolation, honest verification and single-source coverage."""
import importlib.util,json,subprocess,sys
from pathlib import Path
import pytest
from tests.challenges.conftest import repo_root
ROOT=repo_root();ENTRY=ROOT/'scripts/challenge-v2.py'
def cli(*args):return subprocess.run([sys.executable,str(ENTRY),*map(str,args)],capture_output=True,text=True,cwd=ROOT)

def test_prepare_refuses_existing_attempt_and_reset_is_new_copy(tmp_path):
 w=tmp_path/'attempt';p=cli('prepare','git','phase-one-certified','--workspace',w);assert p.returncode==0,p.stdout+p.stderr
 (w/'contract.md').write_text('Learner-owned change')
 assert cli('prepare','git','phase-one-certified','--workspace',w).returncode!=0
 assert cli('reset','git','phase-one-certified','--workspace',w).returncode!=0
 assert (w/'contract.md').read_text()=='Learner-owned change'
 other=tmp_path/'new-attempt';assert cli('reset','git','phase-one-certified','--workspace',other).returncode==0
 assert 'Grain:' in (other/'contract.md').read_text()

def test_inactive_unknown_and_implicit_solution_verification_rejected(tmp_path):
 for tool,phase in [('kafka','phase-two-proficient'),('databricks-cli','phase-two-proficient'),('unknown','phase-one-certified')]:
  assert cli('prepare',tool,phase,'--workspace',tmp_path/tool).returncode!=0
 assert cli('verify','git','phase-one-certified').returncode!=0

def test_dry_run_never_creates_workspace(tmp_path):
 w=tmp_path/'future';assert cli('prepare','git','phase-one-certified','--workspace',w,'--dry-run').returncode==0
 assert not w.exists()

def test_manifest_readme_coverage_timing_and_explicit_optional_routes():
 m=json.loads((ROOT/'challenges/v2/manifest.json').read_text());actual={str(p.relative_to(ROOT/'challenges/v2')) for p in (ROOT/'challenges/v2').rglob('README.md')}
 assert set(m['readme_order'])==actual and len(m['readme_order'])==len(actual)
 offered=0
 for t in m['tools']:
  for p in t['phases']:
   assert (ROOT/'challenges/v2'/p['starter']).is_dir()
   assert p['optional']==(t['id']=='kafka')
   if not p['offered']:assert not p['tasks'];continue
   offered+=1;lo=sum(x['estimate_minutes']['low'] for x in p['tasks']);hi=sum(x['estimate_minutes']['high'] for x in p['tasks'])
   assert (lo,hi)==(p['estimate_minutes']['low'],p['estimate_minutes']['high'])
   assert 45<=lo<=hi<=120
   text=(ROOT/'challenges/v2'/p['readme']).read_text()
   for task in p['tasks']:
    assert ('{#'+task['id']+'}' in text or '<a id="'+task['id']+'"></a>' in text) and task['concept_ids'][0] in text
 assert offered==12

def test_event_validation_rejects_conflicting_dataset_and_missing_identity():
 spec=importlib.util.spec_from_file_location('bridge',ROOT/'scripts/v2_kafka_bridge.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 e=json.loads((ROOT/'challenges/v2/kafka/phase-one-certified/starter/event.json').read_text());assert b.validate_event(e)==e
 assert b.run_id(e)==b.run_id(dict(e))
 for bad in [{**e,'event_id':'../../unsafe'},{**e,'location':'/arbitrary/path'},{**e,'dataset_version':'other'}, {k:v for k,v in e.items() if k!='arrived_at'}]:
  with pytest.raises(ValueError):b.validate_event(bad)

@pytest.mark.skipif(__import__('shutil').which('pandoc') is None,reason='sync-v2-course.py parses READMEs with pandoc, which is not on PATH')
def test_changed_phase_title_cannot_leave_instructor_summary_stale(tmp_path):
 import shutil
 sandbox=tmp_path/'client';(sandbox/'scripts').mkdir(parents=True)
 shutil.copy2(ROOT/'scripts/sync-v2-course.py',sandbox/'scripts/sync-v2-course.py')
 shutil.copytree(ROOT/'challenges/v2',sandbox/'challenges/v2')
 f=sandbox/'challenges/v2/git/phase-one-certified/README.md'
 f.write_text(f.read_text().replace('git-p1-01: Inspect the three working states','git-p1-01: A changed learner outcome'))
 result=subprocess.run([sys.executable,str(sandbox/'scripts/sync-v2-course.py'),'--check'],capture_output=True,text=True)
 assert result.returncode!=0
 assert 'Phase title/manifest drift' in result.stderr
 assert not (sandbox/'designer/generated').exists()

def test_learner_git_repository_in_documented_lab_subfolder_is_verifiable(tmp_path):
 import shutil
 w=tmp_path/'learner';shutil.copytree(ROOT/'challenges/v2-solutions/git/phase-one-certified/solution',w)
 result=subprocess.run(['bash','workflow.sh'],cwd=w,capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
 (w/'workflow.sh').unlink()
 result=cli('verify','git','phase-one-certified','--workspace',w)
 assert result.returncode==0,result.stdout+result.stderr
 assert 'local_history' in result.stdout
