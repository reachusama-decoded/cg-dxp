#!/usr/bin/env python3
"""Fresh instructor-agent reconstruction and two-workspace local dbt rehearsal.
Prior solution exposure is disclosed; this is not a junior learner timing pilot.
"""
import argparse,csv,hashlib,json,os,shutil,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run-id',required=True);a=ap.parse_args()
    base=ROOT/'.local/classroom-rehearsal'/a.run_id
    if base.exists():raise SystemExit('Fresh run ID required')
    base.mkdir(parents=True);dbt=os.environ.get('V2_DBT_BIN',str(ROOT/'.local/v2-tools/bin/dbt'));python=os.environ.get('V2_PYTHON_BIN',str(ROOT/'.local/v2-tools/bin/python'))
    records=[]
    def run(cmd,cwd,label,expected=0):
        start=time.monotonic();env={**os.environ,'V2_DB_PATH':str(cwd/'training.duckdb'),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}
        p=subprocess.run([str(x) for x in cmd],cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        log=base/(label+'.log');log.write_text(p.stdout);r={'label':label,'command':[str(x) for x in cmd],'expected_exit':expected,'exit_code':p.returncode,'duration_seconds':round(time.monotonic()-start,3),'raw_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()};records.append(r)
        assert p.returncode==expected,p.stdout
        return p.stdout
    # Reconstruct from the learner starter and its explicit five task contracts.
    w=base/'learner reconstruction';shutil.copytree(ROOT/'challenges/v2/dbt/phase-one-certified/starter',w)
    run([dbt,'--version'],w,'version');run([dbt,'debug','--profiles-dir','.'],w,'debug');run([dbt,'seed','--profiles-dir','.'],w,'seed')
    (w/'models/stg_holdings.sql').write_text("select fund_id,instrument_id,cast(market_value as decimal(18,2)) as market_value from {{ source('training','holdings') }}\n")
    (w/'models/stg_funds.sql').write_text("select fund_id,fund_name from {{ source('training','funds') }}\n")
    (w/'models/starter_status.sql').unlink()
    run([dbt,'run','--select','stg_holdings','stg_funds','--profiles-dir','.'],w,'staging')
    (w/'models/fund_exposure.sql').write_text("select f.fund_id,f.fund_name,count(h.instrument_id) as holdings,coalesce(sum(h.market_value),0) as exposure from {{ ref('stg_funds') }} f left join {{ ref('stg_holdings') }} h using(fund_id) group by f.fund_id,f.fund_name\n")
    run([dbt,'run','--select','+fund_exposure','--profiles-dir','.'],w,'mart')
    (w/'models/schema.yml').write_text("""version: 2
models:
  - name: stg_funds
    columns:
      - name: fund_id
        data_tests: [unique, not_null]
  - name: stg_holdings
    columns:
      - name: fund_id
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('stg_funds')
                field: fund_id
  - name: fund_exposure
    columns:
      - name: fund_id
        data_tests: [unique, not_null]
""")
    (w/'tests').mkdir(exist_ok=True);(w/'tests/total_exposure.sql').write_text("select 1 as failed where abs((select sum(exposure) from {{ ref('fund_exposure') }})-250)>0.001\n")
    run([dbt,'build','--profiles-dir','.'],w,'completed-build');run([python,ROOT/'scripts/demo-checks.py','exposure','--workspace',w],w,'independent-output')
    run([sys.executable,ROOT/'scripts/challenge-v2.py','verify','dbt','phase-one-certified','--workspace',w,'--mode','offline'],ROOT,'completion-verifier')
    # New shells/executable invocations restore only documented cwd/profile, not
    # a preceding shell's exports. Explicit absolute runtime is instructor prep.
    run([dbt,'build','--profiles-dir','.'],w,'new-shell-replay')
    def journey(label):
        target=base/label;shutil.copytree(w,target,ignore=shutil.ignore_patterns('training.duckdb*','target','logs','.user.yml'))
        run([dbt,'seed','--profiles-dir','.'],target,label+'-seed');run([dbt,'build','--profiles-dir','.'],target,label+'-build')
        run([python,ROOT/'scripts/demo-checks.py','exposure','--workspace',target],target,label+'-oracle')
        return target
    with ThreadPoolExecutor(max_workers=2) as pool:one,two=list(pool.map(journey,['learner-a','learner-b']))
    (one/'training.duckdb').unlink();run([python,ROOT/'scripts/demo-checks.py','exposure','--workspace',two],two,'learner-b-after-a-cleanup')
    report={'run_id':a.run_id,'boundary':'local dbt/DuckDB only','reconstruction':'Authored from fresh learner starter and phase task contracts; instructor solution inspected earlier, so independence is limited','two_workspaces':'Concurrent seed/build/independent query; deleting A database leaves B correct','reconnect':'Separate processes restore explicit runtime and cwd/profile; no prior activated shell used','records':records,'owned_resources':'Only this fresh private rehearsal directory and its databases; A DB removed, B/reconstruction retained for evidence','human_learner_pilot':'unavailable; durations are agent/tool execution, not learner completion estimates','docker_astro_connected_isolation':'pending real environment','disk_bytes':sum(p.stat().st_size for p in base.rglob('*') if p.is_file())}
    report['source_hashes']={rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in ['challenges/v2/manifest.json','challenges/v2/dbt/phase-one-certified/README.md','scripts/challenge-v2.py','scripts/demo-checks.py','instructor-demos/rehearse-local.py']}
    out=ROOT/'designer/reviews/live-dev-container'/a.run_id;out.mkdir(parents=True,exist_ok=True);(out/'local-classroom-rehearsal.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
