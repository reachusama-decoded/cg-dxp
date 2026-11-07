"""Consequential evidence and session contracts; fixtures never stand in for tool pilots."""
import copy,json,os,signal,subprocess,sys,time
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from instructor_demos.contracts import bindings,inside,load_story
from instructor_demos.runner import assertion,capture,check_capture
from instructor_demos.terminal import Terminal
from instructor_demos.publish import export,vtt_time

@pytest.fixture
def fixture_root(tmp_path):
    # Small source-bound shell story for runner acceptance, explicitly test-only.
    import shutil
    root=tmp_path/'client';root.mkdir()
    for rel in ['instructor-demos/schema','instructor-demos/theme','scripts/instructor_demos']:
        shutil.copytree(ROOT/rel,root/rel,ignore=shutil.ignore_patterns('__pycache__'))
    for rel in ['scripts/demo-checks.py','scripts/instructor-demos.py','instructor-demos/requirements.lock']:
        (root/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,root/rel)
    (root/'challenges/v2').mkdir(parents=True);(root/'challenges/v2/manifest.json').write_text(json.dumps({'tools':[{'phases':[{'tasks':[{'id':'git-p1-01'}]}]}]}))
    (root/'input.txt').write_text('owned synthetic test input')
    story={'schema_version':1,'id':'test-observation','title':'Test observation','objective':'Test only','tool':'git','task_ids':['git-p1-01'],'route':'local-test','readiness':'ready','audience':'test only','prerequisites':'bash and local browser','source_inputs':['input.txt'],'requires':['browser'],'resources':['private test workspace'],'cleanup':['rm -f owned-marker'],'main_book':{'include':False,'teaching_key':'test'},'steps':[{'id':'observe','action':{'adapter':'terminal','session':'developer','command':'echo observed; touch owned-marker'},'expect':{'exit_code':0,'checks':[{'kind':'output-contains','text':'observed'},{'kind':'file-present','path':'owned-marker'}]},'capture':{'context':'LOCAL TEST TERMINAL','hold_seconds':0},'caption':{'action':'Observe test output','notice':'Test output only'}}],'closing_question':'What was observed?'}
    p=root/'instructor-demos/stories/test-observation/story.yaml';p.parent.mkdir(parents=True)
    import yaml
    p.write_text(yaml.safe_dump(story));return root,p,story

def test_persistent_pty_cwd_variables_and_real_nonzero_exit(tmp_path):
    t=Terminal(tmp_path,os.environ)
    try:
        assert t.run('export OBSERVED=retained; mkdir child; cd child')['exit_code']==0
        result=t.run('printf "%s %s\\n" "$OBSERVED" "$(basename "$PWD")"; test -e absent')
        assert result['exit_code']==1 and 'retained child' in result['output']
        assert '\x1eDEMO_' not in t.display
    finally:t.close()

def test_nested_interactive_shell_keeps_real_state(tmp_path):
    t=Terminal(tmp_path,os.environ)
    try:
        t.run('bash --noprofile --norc -i',complete=False,wait_for=r'demo \$',timeout=5)
        assert t.run('export INSIDE=child; echo "$INSIDE"')['exit_code']==0
        assert 'child' in t.run('echo "$INSIDE"')['output']
        t.run('exit',complete=False,wait_for='exit',timeout=5)
        result=t.run('echo "${INSIDE:-parent}"')
        assert result['exit_code']==0 and 'parent' in result['output']
    finally:t.close()

def test_missing_prerequisite_is_blocked_without_frames(fixture_root,monkeypatch):
    root,p,s=fixture_root;s['requires']=['env:DEMO_TEST_MISSING'];monkeypatch.delenv('DEMO_TEST_MISSING',raising=False)
    import yaml;p.write_text(yaml.safe_dump(s))
    result=capture(root,p,s,'blocked')
    assert result['status']=='blocked' and result['checkpoints']==[]
    assert not (root/'.local/instructor-demos/blocked/test-observation').exists()
    with pytest.raises(ValueError):export(root,[(p,s,result)],root/'candidate')
    assert not (root/'candidate').exists()

def test_capture_observed_frame_video_and_owned_cleanup(fixture_root):
    root,p,s=fixture_root;result=capture(root,p,s,'real-test')
    assert result['status']=='captured',result.get('reason')
    assert len(result['checkpoints'])==1 and result['videos']
    assert result['cleanup'][0]['exit_code']==0
    assert not (Path(result['private_artifacts']['path'])/'workspace/owned-marker').exists()
    assert check_capture(root,p,s,result)
    # Unreviewed evidence cannot produce even a partial publishing directory.
    with pytest.raises(ValueError,match='review'):export(root,[(p,s,result)],root/'unreviewed')
    assert not (root/'unreviewed').exists()
    (root/'input.txt').write_text('changed source')
    with pytest.raises(ValueError,match='Stale'):check_capture(root,p,s,result)

def test_corrupted_capture_is_rejected(fixture_root):
    root,p,s=fixture_root;result=capture(root,p,s,'tamper-test')
    work=Path(result['private_artifacts']['path']);(work/result['checkpoints'][0]['frame']).write_bytes(b'wrong bytes')
    with pytest.raises(ValueError,match='bytes changed'):check_capture(root,p,s,result)

def test_wrong_failure_reason_cannot_be_accepted(tmp_path):
    with pytest.raises(AssertionError,match='diagnostic'):
        assertion(ROOT,tmp_path,{'kind':'output-contains','text':'relationship failed'},{'exit_code':1,'output':'missing executable'}, {})

def test_wrong_workspace_cannot_supply_file_evidence(tmp_path):
    (tmp_path/'other').mkdir();(tmp_path/'other/receipt.json').write_text('{}')
    (tmp_path/'attempt').mkdir()
    with pytest.raises(AssertionError):assertion(ROOT,tmp_path/'attempt',{'kind':'file-present','path':'receipt.json'},{}, {})
    with pytest.raises(ValueError,match='escapes'):inside(tmp_path/'attempt','../other/receipt.json')

def test_dry_run_does_not_create_working_state(fixture_root):
    root,p,s=fixture_root;result=capture(root,p,s,'dry',dry_run=True)
    assert result['actions']==s['steps'] and not (root/'.local').exists()

def test_schema_rejects_unknown_field_and_duplicate_checkpoint(fixture_root):
    root,p,s=fixture_root
    import yaml,jsonschema
    s['invented']=True;p.write_text(yaml.safe_dump(s))
    with pytest.raises(jsonschema.ValidationError):load_story(root,p)
    del s['invented'];s['steps'].append(copy.deepcopy(s['steps'][0]));p.write_text(yaml.safe_dump(s))
    with pytest.raises(ValueError,match='Duplicate'):load_story(root,p)

def test_caption_timestamps_retain_millisecond_precision():
    assert vtt_time(62.345)=='00:01:02.345'

def test_interruption_closes_pty_and_cleans_only_owned_files(fixture_root,monkeypatch):
    root,p,s=fixture_root
    from instructor_demos import runner
    original=runner.Terminal.run
    def interrupt(self,*args,**kwargs):
        original(self,*args,**kwargs)
        raise KeyboardInterrupt
    monkeypatch.setattr(runner.Terminal,'run',interrupt)
    with pytest.raises(KeyboardInterrupt):capture(root,p,s,'interrupted')
    result=json.loads((root/'designer/reviews/instructor-demos/interrupted/test-observation/capture-manifest.json').read_text())
    assert result['status']=='interrupted' and result['cleanup'][0]['exit_code']==0
    assert not (Path(result['private_artifacts']['path'])/'workspace/owned-marker').exists()
    assert (root/'input.txt').read_text()=='owned synthetic test input'

def test_background_process_in_owned_terminal_session_is_stopped(tmp_path):
    import re
    t=Terminal(tmp_path,os.environ)
    result=t.run('sleep 120 & printf "CHILD=%s\\n" "$!"')
    child=int(re.search(r'CHILD=(\d+)',result['output'])[1]);t.close()
    def active():
        try:return Path(f'/proc/{child}/stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
        except FileNotFoundError:return False
    deadline=time.monotonic()+2
    while active() and time.monotonic()<deadline:time.sleep(.01)
    assert not active()

def test_legacy_answer_separation_preserves_body_and_code_literals():
    import importlib.util
    spec=importlib.util.spec_from_file_location('separation',ROOT/'scripts/separate-v2-stretch-answers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    text='# Question\n\n<details><summary>Solution</summary>\n\n```python\nprint("</details>")\n```\n\nExplain this answer.\n</details>\n\nKeep this learner hint.\n'
    learner,answers=module.transform(text,'dbt')
    assert len(answers)==1 and 'print("</details>")' in answers[0]['body']
    assert 'Keep this learner hint.' in learner and 'Explain this answer.' not in learner

def test_package_inventory_excludes_capture_answers_and_private_runtime(tmp_path):
    import importlib.util
    spec=importlib.util.spec_from_file_location('packager',ROOT/'scripts/package-v2.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    sources=module.inventory()
    assert not any('.local' in p.relative_to(ROOT).parts or p.name=='.databrickscfg' for p in sources)
    # Full archive acceptance is exercised separately after source stabilization.
    assert 'instructor-demos' in module.INSTRUCTOR_DIRS and 'v2-solutions' in module.INSTRUCTOR_DIRS

def test_portable_server_returns_exact_bounded_ranges(tmp_path):
    import functools,http.server,importlib.util,threading,urllib.request,urllib.error
    spec=importlib.util.spec_from_file_location('ranges',ROOT/'scripts/serve-instructor-demos.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    (tmp_path/'recording.webm').write_bytes(b'0123456789')
    class Quiet(module.RangeHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(tmp_path)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        url=f'http://127.0.0.1:{server.server_port}/recording.webm'
        for requested,expected,description in [('bytes=2-4',b'234','bytes 2-4/10'),('bytes=-3',b'789','bytes 7-9/10'),('bytes=8-',b'89','bytes 8-9/10')]:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':requested})) as response:
                assert response.status==206 and response.read()==expected
                assert response.headers['Content-Range']==description
        with pytest.raises(urllib.error.HTTPError) as e:urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=20-'}))
        assert e.value.code==416
    finally:server.shutdown();server.server_close();thread.join()
