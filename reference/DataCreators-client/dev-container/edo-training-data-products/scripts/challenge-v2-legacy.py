#!/usr/bin/env python3
"""Version-explicit workspace and evidence interface. No writes to v1/products."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'challenges/legacy-fixtures/2026-10-08/v2'; S=ROOT/'challenges/legacy-fixtures/2026-10-08/v2-solutions'
class Blocked(Exception): pass
CONNECTED=None  # set by --mode live: the Databricks route replaces the local DuckDB route

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory(path):
    return {str(p.relative_to(path)):digest(p) for p in sorted(path.rglob('*')) if p.is_file() and not any(a in p.parts for a in ['target','logs','__pycache__','.git','.venv']) and not p.name.endswith(('.duckdb','.wal'))}
def run(cmd,cwd,env=None,expected=0):
    p=subprocess.run([str(x) for x in cmd],cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
    print(p.stdout,end='')
    if p.returncode!=expected: raise AssertionError(f'{cmd[0]} returned {p.returncode}, expected {expected}')
    return p.stdout

def executable(name,local=None):
    p=Path(os.environ.get('V2_'+name.upper().replace('-','_')+'_BIN',str(ROOT/local) if local else ''))
    if p.is_file(): return str(p.absolute())
    q=shutil.which(name)
    if q:return q
    raise Blocked(f'{name} unavailable; prepare the declared execution boundary')

def connected_route():
    missing=[k for k in ['DATABRICKS_HOST','DBT_HTTP_PATH','DBT_ACCESS_TOKEN','V2_DB_SCHEMA'] if not os.environ.get(k) or os.environ[k].startswith('MISSING_')]
    if missing:raise Blocked('Connected Databricks route needs '+', '.join(missing)+': run under `mise exec --` after `mise run setup:databricks`, and set V2_DB_SCHEMA to the assigned schema')
    dbt=os.environ.get('V2_DBT_DATABRICKS_BIN') or shutil.which('dbt')
    version=subprocess.run([dbt,'--version'],capture_output=True,text=True).stdout if dbt else ''
    if 'databricks' not in version:raise Blocked('No dbt executable with the databricks adapter on PATH; set V2_DBT_DATABRICKS_BIN')
    return {'dbt':dbt,'cli':executable('databricks'),'catalog':os.environ.get('DBT_CATALOG','training_dev'),'schema':os.environ['V2_DB_SCHEMA'],'warehouse_id':os.environ['DBT_HTTP_PATH'].rstrip('/').rsplit('/',1)[-1],'dbt_version':version.split('installed:',1)[-1].split()[0] if 'installed:' in version else version.strip()}

def databricks_query(sql):
    """Statement Execution API; values typed like the DuckDB route (decimals stay strings)."""
    c=CONNECTED;api=lambda *a:json.loads(subprocess.run([c['cli'],'api',*a,'--output','json'],text=True,capture_output=True,check=True,timeout=120).stdout)
    r=api('post','/api/2.0/sql/statements','--json',json.dumps({'statement':sql,'warehouse_id':c['warehouse_id'],'catalog':c['catalog'],'schema':c['schema'],'wait_timeout':'50s','on_wait_timeout':'CONTINUE','format':'JSON_ARRAY','disposition':'INLINE'}))
    deadline=time.monotonic()+600
    while r['status']['state'] in ('PENDING','RUNNING'):
        if time.monotonic()>deadline:raise TimeoutError('Statement did not finish: '+sql)
        time.sleep(3);r=api('get','/api/2.0/sql/statements/'+r['statement_id'])
    if r['status']['state']!='SUCCEEDED':raise AssertionError(f"{r['status']}: {sql}")
    types=[x['type_name'] for x in r['manifest']['schema'].get('columns',[])];result=r.get('result',{});rows=list(result.get('data_array') or [])
    while result.get('next_chunk_index') is not None:
        result=api('get',f"/api/2.0/sql/statements/{r['statement_id']}/result/chunks/{result['next_chunk_index']}");rows+=result.get('data_array') or []
    def typed(v,t):
        if v is None or t in ('DECIMAL','STRING','DATE','TIMESTAMP'):return v
        if t in ('INT','LONG','SHORT','BYTE'):return int(v)
        if t in ('FLOAT','DOUBLE'):return float(v)
        return v=='true' if t=='BOOLEAN' else v
    return [[typed(v,t) for v,t in zip(row,types)] for row in rows]

CHECKED=['fund_exposure','arrival_ledger','rpt_portfolio_summary','rpt_portfolio_performance','rpt_advisor_leaderboard','rpt_region_report','dom_portfolio__portfolio','dom_party__advisor']
def drop_checked_relations():
    """A shared schema keeps relations from earlier runs; drop the ones the checks read so a missing model can't pass."""
    names=','.join(repr(n) for n in CHECKED)
    for name,kind in databricks_query(f"select table_name,table_type from information_schema.tables where table_schema='{CONNECTED['schema']}' and table_name in ({names})"):
        databricks_query(f"drop {'view' if kind=='VIEW' else 'table'} if exists {CONNECTED['catalog']}.{CONNECTED['schema']}.{name}")
    return CHECKED

def dbt_command(w,*args,expected=0):
    if CONNECTED:
        env={**os.environ,'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}
        return run([CONNECTED['dbt'],*args,'--target','databricks','--project-dir',w,'--profiles-dir',w],w,env,expected)
    dbt=executable('dbt','.local/v2-tools/bin/dbt')
    env={**os.environ,'V2_DB_PATH':str(w/'training.duckdb'),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}
    return run([dbt,*args,'--project-dir',w,'--profiles-dir',w],w,env,expected)

def query(w,sql):
    if CONNECTED:return databricks_query(sql)
    python=executable('python','.local/v2-tools/bin/python')
    code='import duckdb,json,sys; c=duckdb.connect(sys.argv[1],read_only=True); print(json.dumps(c.execute(sys.argv[2]).fetchall(),default=str))'
    result=subprocess.run([python,'-c',code,str(w/'training.duckdb'),sql],text=True,capture_output=True,check=True)
    return json.loads(result.stdout)

def exposure(w):
    from decimal import Decimal
    holdings=list(csv.DictReader((w/'seeds/holdings.csv').open()))
    funds=list(csv.DictReader((w/'seeds/funds.csv').open()))
    expected={r['fund_id']:[0,Decimal(0)] for r in funds}
    assert len(expected)==len(funds),'Duplicate fund keys'
    assert len({(r['fund_id'],r['instrument_id']) for r in holdings})==len(holdings),'Duplicate holding grain'
    for r in holdings:
        assert r['fund_id'] in expected,'Unmatched fund key'
        expected[r['fund_id']][0]+=1;expected[r['fund_id']][1]+=Decimal(r['market_value'])
    rows=query(w,'select fund_id,holdings,exposure from fund_exposure order by fund_id')
    assert len(rows)==len(expected) and {f:[n,Decimal(str(v))] for f,n,v in rows}==expected,rows
    staged=query(w,'select fund_id,instrument_id,market_value from stg_holdings')
    assert len(staged)==len(holdings) and {(f,i,Decimal(str(v))) for f,i,v in staged}=={(r['fund_id'],r['instrument_id'],Decimal(r['market_value'])) for r in holdings},'Staging grain/value loss'
    # Databricks data_type omits precision; full_data_type retains it.
    # Scope metadata to this route so another schema cannot supply the type.
    type_column='full_data_type' if CONNECTED else 'data_type'
    schema=(CONNECTED['schema'] if CONNECTED else 'main').replace("'", "''")
    types=query(w,f"select {type_column} from information_schema.columns where table_schema='{schema}' and table_name='stg_holdings' and column_name='market_value'")
    assert len(types)==1 and str(types[0][0]).upper().replace(' ','')=='DECIMAL(18,2)','Money contract must remain decimal(18,2)'
    return rows

def oracle_atlas(w):
    """Independent raw CSV reference with Decimal and tuple keys, no model SQL reuse."""
    from decimal import Decimal
    def rows(name):return list(csv.DictReader((w/'seeds'/f'{name}.csv').open()))
    raw=rows('trades'); trades=[t for t in raw if int(t['qty'])>0 and int(t['price_cents'])>0 and t['side'] in ['B','S']]
    assert len(raw)==10000 and len(trades)==9880
    dims={name:{int(r[key]):r for r in rows(name) if int(r[key])>0} for name,key in [('portfolios','portfolio_id'),('clients','client_id'),('advisors','advisor_id'),('instruments','instrument_id')]}
    prices={}
    for t in trades:
        i=int(t['instrument_id']); key=(int(t['ts']),int(t['trade_id']))
        if i not in prices or key>prices[i][0]:prices[i]=(key,Decimal(t['price_cents'])/100)
    positions={}
    for t in trades:
        key=(int(t['portfolio_id']),int(t['instrument_id']));d=positions.setdefault(key,{'qty':Decimal(0),'fees':Decimal(0),'trades':0,'buy':Decimal(0),'sell':Decimal(0)})
        qty=Decimal(t['qty']);gross=qty*Decimal(t['price_cents'])/100
        d['qty']+=qty if t['side']=='B' else -qty;d['fees']+=gross*Decimal(t['fee_bps'])/10000;d['trades']+=1;d['buy' if t['side']=='B' else 'sell']+=gross
    expected={}
    for (pf,i),d in positions.items():
        assert i in dims['instruments'] and pf in dims['portfolios']
        portfolio=dims['portfolios'][pf];client=int(portfolio['client_id']);advisor=int(portfolio['advisor_id'])
        assert client in dims['clients'] and advisor in dims['advisors']
        s=expected.setdefault(pf,{'aum':Decimal(0),'fees':Decimal(0),'trades':0,'positions':0,'buy':Decimal(0),'sell':Decimal(0),'client':client,'advisor':advisor,'region':dims['advisors'][advisor]['region']})
        s['aum']+=d['qty']*prices[i][1];s['fees']+=d['fees'];s['trades']+=d['trades'];s['positions']+=1;s['buy']+=d['buy'];s['sell']+=d['sell']
    actual=query(w,'select portfolio_id,client_id,advisor_id,aum,fees_paid,trades,positions from rpt_portfolio_summary order by portfolio_id')
    assert len(positions)==3717 and len(expected)==1028 and len(actual)==1028
    for pf,client,advisor,aum,fee,count,pos in actual:
        s=expected[pf];assert (client,advisor,count,pos)==(s['client'],s['advisor'],s['trades'],s['positions'])
        assert abs(Decimal(str(aum))-s['aum'])<Decimal('0.01'),pf
        assert abs(Decimal(str(fee))-s['fees'])<Decimal('0.01'),pf
    assert len(dims['portfolios'])-len(expected)==1472
    return expected

def atlas_advanced(w,expected):
    from decimal import Decimal
    perf=query(w,'select portfolio_id,buy_value,sell_value,net_flow,fee_bps_realized from rpt_portfolio_performance')
    assert len(perf)==1028
    for pf,buy,sell,net,rate in perf:
        s=expected[pf]
        for actual,key in [(buy,'buy'),(sell,'sell')]:assert abs(Decimal(str(actual))-s[key])<Decimal('.01')
        assert abs(Decimal(str(net))-(s['buy']-s['sell']))<Decimal('.01')
        denominator=s['buy']+s['sell'];assert denominator>0
        assert abs(Decimal(str(rate))-(s['fees']/denominator*10000))<Decimal('.0001')
    assert query(w,'select 1.0 / nullif(0,0)')==[[None]]
    advisors={};regions={}
    for s in expected.values():
        a=advisors.setdefault(s['advisor'],{'aum':Decimal(0),'fees':Decimal(0),'portfolios':0,'region':s['region']});a['aum']+=s['aum'];a['fees']+=s['fees'];a['portfolios']+=1
    ranks={v:i+1 for i,v in enumerate(sorted({x['aum'] for x in advisors.values()},reverse=True))}
    actual=query(w,'select advisor_id,region,book_aum,fees_generated,portfolios,rank from rpt_advisor_leaderboard')
    assert len(actual)==len(advisors)
    for aid,region,value,fees,count,rank in actual:
        s=advisors[aid];assert (region,count,rank)==(s['region'],s['portfolios'],ranks[s['aum']]);assert abs(Decimal(str(value))-s['aum'])<Decimal('.01');assert abs(Decimal(str(fees))-s['fees'])<Decimal('.01')
    for a in advisors.values():
        r=regions.setdefault(a['region'],{'aum':Decimal(0),'fees':Decimal(0),'portfolios':0,'advisors':0});r['aum']+=a['aum'];r['fees']+=a['fees'];r['portfolios']+=a['portfolios'];r['advisors']+=1
    actual=query(w,'select region,advisors,portfolios,aum,fees_generated from rpt_region_report');assert len(actual)==len(regions)
    for region,ac,pc,aum,fee in actual:
        s=regions[region];assert (ac,pc)==(s['advisors'],s['portfolios']);assert abs(Decimal(str(aum))-s['aum'])<Decimal('.01');assert abs(Decimal(str(fee))-s['fees'])<Decimal('.01')
    assert sorted(query(w,"select dense_rank() over(order by v desc) from (values(10),(10),(5)) t(v)"))==[[1],[1],[2]]
    return {'advisor_rows':len(advisors),'region_rows':len(regions),'portfolio_rows':len(expected)}

def verify_dbt(w,phase,starter,tool):
    # A shared schema keeps earlier relations; rebuild them so no output predates this run.
    fresh=['--full-refresh'] if CONNECTED else []
    if CONNECTED:drop_checked_relations()
    dbt_command(w,'seed',*fresh);dbt_command(w,'build',*fresh)
    if starter:return {'baseline':'seed/build executed','completion':False}
    if tool=='capstone':
        expected=oracle_atlas(w);out={'valid_trades':9880,'positions':3717,'active_portfolios':1028,'inactive_portfolios':1472,'oracle':'raw CSV Decimal per-key independent computation'}
        # Wrong-key join must visibly lose portfolios; the oracle rejects it.
        defective=query(w,'select count(*) from dom_portfolio__portfolio pf join dom_party__advisor a on pf.client_id=a.advisor_id')[0][0]
        assert defective<2500;out['wrong_key_join_portfolios']=defective
        if phase=='phase-two-proficient':
            out.update(atlas_advanced(w,expected))
            target=w/'models/rpt_region_report.sql';saved=target.read_text()
            target.write_text("select region,count(*) as advisors,sum(portfolios) as portfolios,sum(book_aum) as aum,sum(fees_generated) as fees_generated from {{ ref('rpt_advisor_leaderboard') }} where advisor_id<5 group by region\n")
            dbt_command(w,'run','--select','rpt_region_report')
            dbt_command(w,'test','--select','reconcile_region',expected=1)
            target.write_text(saved);dbt_command(w,'build');atlas_advanced(w,expected)
            out['negative_case']='regional omission failed reconciliation; repaired output rechecked'

        return out
    out={'exposure':exposure(w)}
    if phase=='phase-one-certified':
        # Structural tests and actual behavior both matter: a hard-coded mart
        # with missing relationships must not pass on the happy-path fixture.
        manifest=json.loads((w/'target/manifest.json').read_text())
        tests=[n for n in manifest['nodes'].values() if n['resource_type']=='test']
        for model,column,names in [('stg_funds','fund_id',['unique','not_null']),('stg_holdings','fund_id',['relationships','not_null']),('fund_exposure','fund_id',['unique','not_null'])]:
            for name in names:
                assert any(n.get('test_metadata',{}).get('name')==name and n.get('column_name')==column and any(x.endswith('.'+model) for x in n['depends_on']['nodes']) for n in tests),f'Missing {name} test for {model}.{column}'
        assert any(n.get('test_metadata') is None for n in tests),'Missing singular business check'
        seed=w/'seeds/holdings.csv';original=seed.read_text();seed.write_text(original.replace(',A,',',UNKNOWN,') if ',A,' in original else original.replace('\nA,','\nUNKNOWN,',1))
        assert seed.read_text()!=original,'Negative fixture failed to change a key'
        dbt_command(w,'seed','--select','holdings');dbt_command(w,'run','--select','stg_holdings');dbt_command(w,'test','--select','test_type:generic',expected=1)
        failed=json.loads((w/'target/run_results.json').read_text())['results']
        assert any(r['status']=='fail' and manifest['nodes'][r['unique_id']].get('test_metadata',{}).get('name')=='relationships' for r in failed),'Wrong failure reason'
        seed.write_text(original);dbt_command(w,'seed','--select','holdings');dbt_command(w,'build');exposure(w)
        # Preserve the taught total while moving value between funds. A mart
        # hard-coded to the supplied happy-path answers must be rejected.
        import io
        records=list(csv.DictReader(io.StringIO(original)));fields=list(records[0])
        records[0]['market_value']=str(__import__('decimal').Decimal(records[0]['market_value'])+10)
        other=next(r for r in records if r['fund_id']!=records[0]['fund_id'] and __import__('decimal').Decimal(r['market_value'])>=10)
        other['market_value']=str(__import__('decimal').Decimal(other['market_value'])-10)
        with seed.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(records)
        dbt_command(w,'seed','--select','holdings');dbt_command(w,'build');exposure(w)
        seed.write_text(original);dbt_command(w,'seed','--select','holdings');dbt_command(w,'build');exposure(w)
        out['negative_case']='Unknown fund rejected by relationship test; restored fixture and per-fund output rechecked'
        out['input_sensitivity']='Total-preserving per-fund value change checked against independent CSV oracle; original input restored and rebuilt'
    if phase=='phase-two-proficient':
        dbt_command(w,'run','--select','arrival_ledger');assert query(w,'select count(*),sum(market_value) from arrival_ledger')==[[2,'180.00']]
        dbt_command(w,'run','--select','arrival_ledger');assert query(w,'select count(*) from arrival_ledger')==[[2]]
        # Rewrite the disposable seed, never canonical/learner inputs.
        (w/'seeds/arrivals.csv').write_text('event_id,fund_id,market_value\ne1,A,125\ne2,B,80\ne3,C,20\n')
        dbt_command(w,'seed','--select','arrivals');dbt_command(w,'run','--select','arrival_ledger')
        assert query(w,'select count(*),sum(market_value) from arrival_ledger')==[[3,'225.00']]
        dbt_command(w,'run','--select','arrival_ledger');assert query(w,'select count(*),sum(market_value) from arrival_ledger')==[[3,'225.00']]
        # Observable fan-out from deliberately duplicated fixture, independently calculated.
        h=list(csv.DictReader((w/'seeds/holdings.csv').open()));labels=list(csv.DictReader((w/'fixtures/fund_labels_duplicate.csv').open()))
        joined=[r for r in h for label in labels if r['fund_id']==label['fund_id']]
        assert len(joined)==7 and sum(float(r['market_value']) for r in joined)==400
        # Inject the faulty exposure into a copied runtime, prove SQL reconciliation rejects it, repair.
        original=(w/'models/fund_exposure.sql').read_text()
        (w/'seeds/fund_labels.csv').write_text((w/'fixtures/fund_labels_duplicate.csv').read_text())
        (w/'models/fund_exposure.sql').write_text("select h.fund_id,count(*) as holdings,sum(h.market_value) as exposure from {{ ref('stg_holdings') }} h join {{ ref('fund_labels') }} f using(fund_id) group by h.fund_id\n")
        dbt_command(w,'seed','--select','fund_labels');dbt_command(w,'run','--select','fund_exposure');dbt_command(w,'test','--select','reconcile_exposure',expected=1)
        (w/'models/fund_exposure.sql').write_text(original);dbt_command(w,'build');exposure(w)
        dbt_command(w,'docs','generate');out.update({'incremental_initial':[2,180],'incremental_final':[3,225],'negative_fanout':[7,400],'negative_test':'observed failure then repair'})
    return out

def verify_git(w,phase,starter,mode):
    run(['git','--version'],w)
    assert 'Grain:' in (w/'contract.md').read_text()
    if starter:return {'baseline':'readable contract','completion':False}
    local=w
    if not (w/'workflow.sh').exists():
        candidates=[q for q in [w,*[x for x in w.iterdir() if x.is_dir()]] if (q/'.git').exists()]
        assert len(candidates)==1,'Expected one learner Git repository in the workspace or its immediate lab folder'
        local=candidates[0]
        assert not run(['git','status','--porcelain'],local).strip(),'Uncommitted learner edits'
        text=(local/'contract.md').read_text();assert '09:00 UTC' in text and 'Escalation:' in text and '<<<<<<<' not in text
        run(['git','log','--graph','--oneline','--all'],local)
    else:run(['bash','workflow.sh'],w)
    if phase=='phase-two-proficient' and mode=='live':
        gh=executable('gh');run([gh,'auth','status'],w)
        # Only read existing authorized sandbox evidence; never create/push/message automatically.
        pr=os.environ.get('V2_GITHUB_PR');repo=os.environ.get('V2_GITHUB_REPO')
        if not pr or not repo:raise Blocked('V2_GITHUB_REPO and V2_GITHUB_PR required for read-only real PR evidence')
        data=json.loads(run([gh,'pr','view',pr,'--repo',repo,'--json','url,author,commits,reviews,state,baseRefName,headRefName,headRefOid'],w))
        head=run(['git','rev-parse','HEAD'],local).strip()
        assert data['headRefOid']==head,f"PR head {data['headRefOid'][:7]} is not this workspace's HEAD {head[:7]}"
        assert len(data['commits'])>=2,'A review-response revision (second commit) is required'
        others=[r for r in data['reviews'] if r['author']['login']!=data['author']['login']]
        if not others:raise Blocked(f"{data['url']} has no review from another account; git-p2-03/05 need a real reviewer")
        return {'github_pr':data['url'],'state':data['state'],'head':head,'commits':len(data['commits']),'reviews':len(others)}
    return {'local_history':'commit/branches/merges/conflict/restore executed','remote_evidence':'not assessed' if phase.endswith('proficient') else 'not required', 'completion':not phase.endswith('proficient')}

def verify_docker(w,phase,starter,mode):
    app=w/'app';run([sys.executable,'test_summary.py'],app)
    if mode=='offline':return {'app_oracle':'pass','docker_build_run':'blocked: Docker unavailable in offline mode','completion':False}
    docker=executable('docker');run([docker,'info'],w)
    tag='v2-check-'+str(os.getpid());tags=[]
    try:
        if starter:
            tags.append(tag);run([docker,'build','-t',tag,'.'],w);out=run([docker,'run','--rm',tag],w);assert 'Valid starter' in out
        else:
            for target in (['test','runtime'] if phase.endswith('proficient') else [None]):
                t=tag+('-'+target if target else '');tags.append(t);cmd=[docker,'build','-t',t]
                if target:cmd+=['--target',target]
                run(cmd+['.'],w);out=run([docker,'run','--rm',t],w)
                assert ('summary oracle passed' if target=='test' else '6 holdings, total market value 12,011,626.50') in out
                if target=='runtime':
                    assert run([docker,'run','--rm',t,'id','-u'],w).strip()=='10001'
                    run([docker,'run','--rm',t,'python','-c','from pathlib import Path; assert not Path("/app/test_summary.py").exists()'],w)
        return {'docker_build_run':'pass','starter':starter}
    finally:
        for t in tags:subprocess.run([docker,'image','rm',t],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def verify_cli(w,starter,mode):
    data=json.loads((w/'metadata.json').read_text());assert data['tables'][0]['full_name']=='training_dev.training_learner.holdings';assert data['workspace'][0]['object_type']=='DIRECTORY'
    if mode=='live':
        cli=executable('databricks');profile=os.environ.get('V2_DBX_PROFILE','DEFAULT');run([cli,'--version'],w)
        identity=json.loads(run([cli,'current-user','me','--profile',profile,'--output','json'],w));catalogs=json.loads(run([cli,'catalogs','list','--profile',profile,'--output','json'],w))
        assert identity.get('userName') or identity.get('id');return {'boundary':'live identity/catalog metadata','catalog_response_type':type(catalogs).__name__}
    return {'fixture_parse':'pass','live_access':'not assessed','completion':False}

def verify_airflow(w,phase,starter):
    if starter and phase=='phase-one-certified':
        assert 'Valid starter' in run([sys.executable,'pipeline.py'],w);return {'baseline':'working scaffold','completion':False}
    py=executable('airflow-python','.local/v2-airflow/bin/python')
    dbt=executable('dbt','.local/v2-tools/bin/dbt')
    env={**os.environ,'AIRFLOW_HOME':str(w/'airflow-home'),'AIRFLOW__CORE__LOAD_EXAMPLES':'false','AIRFLOW__CORE__DAGS_FOLDER':str(w),'V2_DBT_BIN':dbt,'V2_DB_PATH':str(w/'project/training.duckdb'),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}
    # A relocated venv can retain launcher shebangs pointing at the old root.
    # Invoke the measured interpreter directly; do not mutate managed launchers.
    run([py,'-m','airflow','db','migrate'],w,env)
    run([py,'-m','airflow','dags','reserialize'],w,env)
    script=ROOT/'scripts/v2-airflow-check.py'
    output=run([py,script,w,'starter' if starter else 'solution'],w,env)
    evidence=[json.loads(line.split('=',1)[1]) for line in output.splitlines() if line.startswith('V2_AIRFLOW_EVIDENCE=')]
    if not starter:assert len(evidence)==1,'Missing fresh Airflow task/run evidence'
    return {'airflow':'actual Dag.test dbt run/quality failure/repair/replay' if not starter else 'actual baseline import','astro_ui':'not assessed','output':exposure(w/'project') if not starter else 'baseline not executed','run_evidence':evidence[0] if evidence else None}

ASTRO_BINDING='''# v2 live binding, generated by scripts/challenge-v2.py and removed after verification.
import os as _v2_os
_v2_os.environ.update({{'V2_DBT_BIN':'/home/astro/.venv/cosmos/bin/dbt','DBT_TARGET':'databricks','V2_DB_SCHEMA':{schema!r},'DBT_HTTP_PATH':_v2_os.environ.get('DATABRICKS_HTTP_PATH',''),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}})
try:
    from airflow.sdk import Connection as _v2_connection
    _v2_conn=_v2_connection.get('databricks_default')
    _v2_os.environ['DBT_ACCESS_TOKEN']=_v2_conn.password or ''
    _v2_os.environ['DATABRICKS_HOST']=(_v2_conn.host or _v2_os.environ.get('DATABRICKS_HOST','')).replace('https://','').replace('http://','').rstrip('/')
except Exception:
    pass
'''

def astro(docker,container,*args,expected=0):
    p=subprocess.run([docker,'exec',container,'airflow',*args],text=True,capture_output=True,timeout=300)
    if p.returncode not in (expected if isinstance(expected,tuple) else (expected,)):raise AssertionError(f'airflow {args[:2]} returned {p.returncode}: {(p.stdout+p.stderr)[-1500:]}')
    return p.stdout

def astro_json(docker,container,*args,expected=0):
    out=astro(docker,container,*args,'-o','json',expected=expected)
    return json.loads(next(line for line in reversed(out.splitlines()) if line[:1] in '[{'))

def verify_airflow_astro(w,phase,starter):
    """Stage the workspace in the Astro DAGs folder, run it on the Astro scheduler/workers against Databricks."""
    docker=executable('docker');names=subprocess.run([docker,'ps','--format','{{.Names}}'],text=True,capture_output=True).stdout.split()
    sched=next((n for n in names if n.endswith('-scheduler-1')),None);proc=next((n for n in names if n.endswith('-dag-processor-1')),None)
    if not sched or not proc:raise Blocked('Astro stack is not running: mise exec -- astro dev start --wait 5m')
    mounts=json.loads(subprocess.run([docker,'inspect',sched,'--format','{{json .Mounts}}'],text=True,capture_output=True).stdout)
    dags=next((Path(m['Source']) for m in mounts if m['Destination']=='/usr/local/airflow/dags'),None)
    if not dags or not dags.exists() or not dags.samefile(ROOT/'data_products'):raise Blocked('The running Astro stack does not mount this project data_products/ as its DAGs folder')
    tag=f"{phase.split('-')[1]}_{os.getpid()}";dag_id='v2_training_pipeline__live_'+tag;stage=ROOT/'data_products'/f'v2_live_{tag}'
    source=(w/'pipeline.py').read_text()
    if source.count("'v2_training_pipeline'")+source.count('"v2_training_pipeline"')!=1:raise AssertionError('Expected exactly one v2_training_pipeline DAG ID to bind a unique Astro DAG ID')
    lines=source.replace("'v2_training_pipeline'",repr(dag_id)).replace('"v2_training_pipeline"',repr(dag_id)).splitlines(keepends=True)
    head=0
    while head<len(lines) and lines[head].startswith('from __future__'):head+=1
    ui=f'http://localhost:6563/dags/{dag_id}'
    try:
        shutil.copytree(w,stage,ignore=shutil.ignore_patterns('airflow-home','*.duckdb*','receipt.json','fail-quality'))
        (stage/'pipeline.py').write_text(''.join(lines[:head])+ASTRO_BINDING.format(schema=CONNECTED['schema'])+''.join(lines[head:]))
        for p in [stage,*stage.rglob('*')]:p.chmod(0o777 if p.is_dir() else 0o666)  # Astro workers run as uid 50000
        astro(docker,proc,'dags','reserialize')
        errors=astro_json(docker,sched,'dags','list-import-errors',expected=(0,1))
        mine=[e for e in errors if stage.name in str(e)]
        assert not mine,f'Astro import error: {mine}'
        tasks=astro(docker,sched,'tasks','list',dag_id).split()
        assert {'prepare','build','quality','publish'}<=set(tasks),tasks
        out={'astro_dag_id':dag_id,'worker_path':f'/usr/local/airflow/dags/{stage.name}','astro_import':'pass'}
        if starter:return out
        drop_checked_relations()
        astro(docker,sched,'dags','unpause',dag_id)
        def run_dag(n):
            rid=f'v2_live_{tag}_{n}_{time.time_ns()}';astro(docker,sched,'dags','trigger',dag_id,'--run-id',rid);deadline=time.monotonic()+1200
            while True:
                state=next((r['state'] for r in astro_json(docker,sched,'dags','list-runs',dag_id) if r['run_id']==rid),None)
                if state in ('success','failed'):break
                if time.monotonic()>deadline:raise TimeoutError(f'{rid} still {state}')
                time.sleep(10)
            tis={t['task_id']:t['state'] for t in astro_json(docker,sched,'tasks','states-for-dag-run',dag_id,rid)}
            print(rid,state,tis);return rid,state,tis
        def task_log(rid,task):
            p=subprocess.run([docker,'exec',sched,'sh','-c',f'cat /usr/local/airflow/logs/dag_id={dag_id}/run_id={rid}/task_id={task}/attempt=*.log'],text=True,capture_output=True)
            return p.stdout
        first,state,tis=run_dag(1);assert state=='success' and set(tis.values())=={'success'},tis
        assert json.loads((stage/'receipt.json').read_text())['run_id']==first;out['success_run']=first;out['output']=exposure(stage/'project')
        (stage/'receipt.json').unlink();(stage/'fail-quality').touch();(stage/'fail-quality').chmod(0o666)
        failed,state,tis=run_dag(2);assert state=='failed' and tis['quality']=='failed' and tis['publish']=='upstream_failed',tis
        assert not (stage/'receipt.json').exists(),'Failure must block publication'
        assert 'Intentional quality drill' in task_log(failed,'quality'),'Quality log lacks the drill failure'
        out['failed_run']=failed;out['failed_states']=tis
        (stage/'fail-quality').unlink()
        repaired,state,tis=run_dag(3);assert state=='success',tis
        assert json.loads((stage/'receipt.json').read_text())['run_id']==repaired;out['repaired_run']=repaired;out['output_after_repair']=exposure(stage/'project')
        out.update({'astro_ui':f'{ui} (runs {first}, {failed}, {repaired}); visual review is separate','connected':{k:CONNECTED[k] for k in ['catalog','schema','warehouse_id']}})
        return out
    finally:
        shutil.rmtree(stage,ignore_errors=True)
        subprocess.run([docker,'exec',proc,'airflow','dags','reserialize'],capture_output=True,timeout=300)
        subprocess.run([docker,'exec',sched,'airflow','dags','delete',dag_id,'-y'],capture_output=True,timeout=300)

def free_port():
    import socket
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def verify_kafka_chain(w,event):
    """Real broker, bridge consume/trigger, isolated Airflow 3.1 standalone run, receipt and DuckDB output."""
    import signal,urllib.request
    docker=executable('docker');py=executable('airflow-python','.local/v2-airflow/bin/python');dbt=executable('dbt','.local/v2-tools/bin/dbt')
    airflow=str(Path(py).parent/'airflow');bridge=str(ROOT/'scripts/v2_kafka_bridge.py')
    compose=w/'compose.yaml' if (w/'compose.yaml').exists() else V/'kafka/phase-one-certified/starter/compose.yaml'
    tag=f'v2-verify-{os.getpid()}';project=tag;port=free_port();out={'compose_project':project,'topic':tag,'group':tag}
    env={**os.environ,'PATH':str(Path(py).parent)+os.pathsep+os.environ.get('PATH',''),'AIRFLOW_HOME':str(w/'airflow-home'),'AIRFLOW__CORE__DAGS_FOLDER':str(w),'AIRFLOW__CORE__LOAD_EXAMPLES':'false','AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION':'false','AIRFLOW__API__PORT':str(port),'AIRFLOW__CORE__EXECUTION_API_SERVER_URL':f'http://127.0.0.1:{port}/execution/','AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL':'5','V2_DBT_BIN':dbt,'V2_DB_PATH':str(w/'project/training.duckdb'),'DBT_SEND_ANONYMOUS_USAGE_STATS':'false'}
    b=lambda *args,expected=0:run([py,bridge,*args,'--topic',tag,'--group',tag],w,env,expected)
    standalone=None
    try:
        up=subprocess.run([docker,'compose','-p',project,'-f',compose,'up','-d','--wait'],text=True,capture_output=True,timeout=300)
        if up.returncode:raise Blocked('Kafka broker did not start (is 127.0.0.1:19092 already in use?): '+up.stderr[-500:])
        for attempt in range(12):
            if subprocess.run([py,bridge,'prepare-topic','--topic',tag,'--timeout','10'],cwd=w,env=env,capture_output=True).returncode==0:break
            time.sleep(5)
        else:raise Blocked('Broker on localhost:19092 never accepted topic creation')
        out['topic_ready']=True
        bad=w/'malformed-event.json';bad.write_text(json.dumps({**event,'location':'/etc/passwd'}))
        run([py,bridge,'validate','--event',bad],w,env,expected=1);out['malformed_rejected']=True
        standalone=subprocess.Popen([airflow,'standalone'],cwd=w,env=env,stdout=open(w/'standalone.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
        deadline=time.monotonic()+300
        while True:
            try:
                if urllib.request.urlopen(f'http://127.0.0.1:{port}/api/v2/monitor/health',timeout=5).status==200 and 'v2_training_pipeline' in subprocess.run([airflow,'dags','list','-o','plain'],env=env,text=True,capture_output=True).stdout:break
            except OSError:pass
            if standalone.poll() is not None or time.monotonic()>deadline:raise Blocked('Isolated Airflow standalone did not become ready: '+(w/'standalone.log').read_text()[-800:])
            time.sleep(5)
        evfile=w/'chain-event.json';evfile.write_text(json.dumps(event))
        common=['--airflow',airflow,'--receipt',str(w/'receipt.json'),'--evidence',str(w/'event-evidence.json')]
        out['produce']=json.loads(b('produce','--event',evfile).strip().splitlines()[-1])
        b('consume',*common);evidence=json.loads((w/'event-evidence.json').read_text());rid=evidence['run_id'];deadline=time.monotonic()+600
        def runs():
            text=subprocess.run([airflow,'dags','list-runs','v2_training_pipeline','-o','json'],env=env,text=True,capture_output=True).stdout
            return json.loads(next((l for l in reversed(text.splitlines()) if l[:1] in '[{'),'[]'))
        while (state:=next((r['state'] for r in runs() if r['run_id']==rid),None)) not in ('success','failed'):
            if time.monotonic()>deadline:raise TimeoutError(f'{rid} still {state}')
            time.sleep(5)
        assert state=='success',state
        run([py,bridge,'verify-chain','--event',evfile,'--receipt',w/'receipt.json','--project',w/'project','--evidence',w/'event-evidence.json'],w,env)
        out.update({'run_id':rid,'partition':evidence['partition'],'offset':evidence['offset'],'decision':evidence['decision'],'output':exposure(w/'project')})
        b('produce','--event',evfile);b('consume',*common);replay=json.loads((w/'event-evidence.json').read_text())
        assert replay['run_id']==rid and replay['decision']=='identical completed run reused' and replay['offset']>evidence['offset'],replay
        assert [r['run_id'] for r in runs()]==[rid],'Replay must not create a second run'
        out['replay']={'offset':replay['offset'],'decision':replay['decision'],'runs':1};exposure(w/'project')
        evfile.write_text(json.dumps({**event,'arrived_at':'2026-10-06T09:00:00Z'}));b('produce','--event',evfile)
        b('consume',*common,expected=1);out['conflict']='same event_id with a different payload rejected; offset left uncommitted'
        return out
    finally:
        if standalone and standalone.poll() is None:
            os.killpg(standalone.pid,signal.SIGTERM)
            try:standalone.wait(60)
            except subprocess.TimeoutExpired:os.killpg(standalone.pid,signal.SIGKILL)
        subprocess.run([docker,'compose','-p',project,'-f',compose,'down','-v'],capture_output=True,timeout=300)

def main():
    global CONNECTED
    ap=argparse.ArgumentParser(description=__doc__,epilog='--mode live: dbt/capstone run the databricks profile target and Airflow runs on the local Astro stack; both need V2_DB_SCHEMA and the mise Databricks environment.')
    ap.add_argument('action',choices=['prepare','reset','verify','verify-solution','verify-starter','list']);ap.add_argument('tool',nargs='?');ap.add_argument('phase',nargs='?');ap.add_argument('--workspace',type=Path);ap.add_argument('--mode',choices=['offline','live'],default='offline');ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args();manifest=json.loads((V/'manifest.json').read_text())
    if a.action=='list':
        for t in manifest['tools']:
            for p in t['phases']:print(t['id'],p['id'],'offered' if p['offered'] else 'not-offered')
        return
    tool=next((t for t in manifest['tools'] if t['id']==a.tool),None)
    phase=next((p for p in tool['phases'] if p['id']==a.phase),None) if tool else None
    if phase is None or not phase['offered']:ap.error('Unknown tool/phase or phase not offered')
    source=V/phase['starter'] if a.action in ['prepare','reset','verify-starter'] else S/a.tool/a.phase/'solution'
    if a.action in ['prepare','reset']:
        dest=(a.workspace or ROOT/'.local/challenges-legacy-2026-10-08'/a.tool/a.phase).resolve()
        if dest.exists():ap.error('Workspace exists; choose --workspace with a new path. Reset never deletes an attempt.')
        if a.dry_run:print(f'Copy {source} to {dest}');return
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(source,dest);print(dest);return
    if a.action=='verify':
        if not a.workspace:ap.error('verify requires --workspace; use verify-solution for instructor reference')
        source=a.workspace.resolve()
    elif a.workspace:source=a.workspace.resolve()
    if not source.is_dir():ap.error('Missing source workspace')
    if a.dry_run:print(json.dumps({'source':str(source),'mode':a.mode,'action':a.action,'writes':'temporary copy only'},indent=2));return
    evidence=ROOT/'.local/v2-evidence';evidence.mkdir(parents=True,exist_ok=True)
    before=inventory(source);stamp=time.time_ns();start=time.monotonic();result='pass';code=0;observations={}
    with tempfile.TemporaryDirectory(prefix='v2-verify-') as tmp:
        w=Path(tmp)/'workspace';shutil.copytree(source,w,ignore=shutil.ignore_patterns('.venv','target','logs','__pycache__','*.duckdb*','airflow-home'))
        starter=a.action=='verify-starter'
        try:
            if a.tool=='git':observations=verify_git(w,a.phase,starter,a.mode)
            elif a.tool=='docker':observations=verify_docker(w,a.phase,starter,a.mode)
            elif a.tool in ['dbt','capstone']:
                if a.mode=='live':CONNECTED=connected_route()
                observations=verify_dbt(w,a.phase,starter,a.tool)
                observations['route']={k:CONNECTED[k] for k in ['catalog','schema','warehouse_id','dbt_version']} if CONNECTED else 'local DuckDB'
            elif a.tool=='databricks-cli':observations=verify_cli(w,starter,a.mode)
            elif a.tool=='airflow':
                if a.mode=='live':
                    if starter and a.phase=='phase-one-certified':raise Blocked('The Phase 1 starter has no DAG yet; the Astro route applies to authored work')
                    CONNECTED=connected_route();observations=verify_airflow_astro(w,a.phase,starter)
                else:observations=verify_airflow(w,a.phase,starter)
            elif a.tool=='kafka':
                sys.path.insert(0,str(ROOT/'scripts'));from v2_kafka_bridge import validate_event
                event=json.loads((w/'event.json').read_text());validate_event(event)
                if a.mode=='live':
                    if starter:raise Blocked('The starter event chain is authored in the learner journey; live mode verifies completed work')
                    observations=verify_kafka_chain(w,event)
                else:observations={'event_contract':'pass','broker_airflow_chain':'not assessed','completion':False}
        except Blocked as e:result='blocked';code=77;observations={'reason':str(e)}
        except Exception as e:
            import traceback;where=traceback.extract_tb(e.__traceback__)[-1]
            result='fail';code=1;observations={'error':str(e) or type(e).__name__,'at':f'{where.name}:{where.lineno}: {where.line}'}
    if result=='pass' and observations.get('completion') is False and (not starter or a.tool=='docker'): result='supporting-only'
    assert before==inventory(source),'Verification changed the supplied source'
    report={'tool':a.tool,'phase':a.phase,'action':a.action,'mode':a.mode,'result':result,'observations':observations,'source_sha256':before,'learner_readme_sha256':digest(V/phase['readme']),'manifest_sha256':digest(V/'manifest.json'),'task_ids':[x['id'] for x in phase['tasks']],'automated_scope':'Behavioral assertions stated in observations; learner explanations and peer review require instructor assessment','verifier_sha256':digest(Path(__file__)),'support_scripts_sha256':{p.name:digest(p) for p in (ROOT/'scripts').glob('v2*') if p.is_file()},'duration_seconds':round(time.monotonic()-start,3),'cleanup':'temporary workspace removed; source hashes unchanged','command':sys.argv,'versions':{}}
    for name,local in [('dbt','.local/v2-tools/bin/dbt'),('airflow-python','.local/v2-airflow/bin/python')]:
        try:
            exe=executable(name,local)
            cmd=[exe,'-m','airflow','version'] if name=='airflow-python' else [exe,'--version']
            measured=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
            report['versions'][name]={'executable':exe,'exit_code':measured.returncode,'output':measured.stdout.strip()}
        except (Blocked,OSError,subprocess.TimeoutExpired) as e:report['versions'][name]={'status':'blocked','reason':str(e)}
    (evidence/f'{a.tool}-{a.phase}-{a.action}-{stamp}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','versions']},indent=2));raise SystemExit(code)
if __name__=='__main__':main()
