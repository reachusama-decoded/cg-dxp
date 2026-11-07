#!/usr/bin/env python3
"""Prepared Databricks/Astro checks. CSV arithmetic is supporting evidence only."""
import argparse, csv, hashlib, json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
BASE = Path(__file__).resolve().parent

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,default=str)+'\n')
def portfolio(seeds):
    h=rows(seeds/'holdings_raw.csv');fx={(r['from_ccy'],r['to_ccy'],r['rate_dt']):Decimal(r['rate']) for r in rows(seeds/'fx_rates_raw.csv')}
    funds={r['fund_cd']:r for r in rows(seeds/'fund_master_raw.csv')};prices={(r['isin'],r['price_dt']):r for r in rows(seeds/'prices_raw.csv')}
    keys=set();out={}
    for r in h:
        key=(r['fund_cd'],r['pos_dt'],r['isin']);assert key not in keys,'Duplicate holding business key';keys.add(key)
        assert r['fund_cd'] in funds,'Unmatched fund';assert (r['isin'],r['pos_dt']) in prices,'Unmatched dated price'
        rate=fx[(r['ccy_cd'],'GBP',r['pos_dt'])];total=Decimal(r['mkt_val_lc'])*rate
        result=out.setdefault((r['fund_cd'],r['pos_dt']),[0,Decimal(0)]);result[0]+=1;result[1]+=total
    return [[f,d,n,v,v/Decimal(100000000)] for (f,d),(n,v) in sorted(out.items())]
def atlas(seeds):
    names={'portfolios':'portfolio_id','clients':'client_id','advisors':'advisor_id','instruments':'instrument_id','funds':'fund_id'}
    dims={name:{int(r[key]):r for r in rows(seeds/(name+'.csv')) if int(r[key])>0} for name,key in names.items()}
    raw=rows(seeds/'trades.csv');valid=[t for t in raw if Decimal(t['qty'])>0 and Decimal(t['price_cents'])>0 and t['side'] in ['B','S']]
    prices={};positions={}
    for t in valid:
        instrument=int(t['instrument_id']);key=(int(t['ts']),int(t['trade_id']))
        if instrument not in prices or key>prices[instrument][0]:prices[instrument]=(key,Decimal(t['price_cents'])/100)
        k=(int(t['portfolio_id']),instrument);p=positions.setdefault(k,[Decimal(0),Decimal(0),0,Decimal(0),Decimal(0)])
        qty=Decimal(t['qty']);p[0]+=qty if t['side']=='B' else -qty;p[1]+=qty*Decimal(t['price_cents'])/100*Decimal(t['fee_bps'])/10000;p[2]+=1;p[3 if t['side']=='B' else 4]+=qty*Decimal(t['price_cents'])/100
    summaries={}
    for (pf,i),(qty,fee,count,buy,sell) in positions.items():
        assert i in dims['instruments'] and pf in dims['portfolios'],'Unmatched trade dimension'
        d=dims['portfolios'][pf];client=int(d['client_id']);advisor=int(d['advisor_id'])
        assert client in dims['clients'] and advisor in dims['advisors'],'Unmatched party dimension'
        s=summaries.setdefault(pf,[client,advisor,Decimal(0),Decimal(0),0,0,Decimal(0),Decimal(0)]);s[2]+=qty*prices[i][1];s[3]+=fee;s[4]+=count;s[5]+=1;s[6]+=buy;s[7]+=sell
    advisors={};regions={}
    for pf,s in summaries.items():
        advisor=s[1];region=dims['advisors'][advisor]['region'];book=advisors.setdefault(advisor,[region,Decimal(0),Decimal(0),0]);book[1]+=s[2];book[2]+=s[3];book[3]+=1
    ranks={v:i+1 for i,v in enumerate(sorted({s[1] for s in advisors.values()},reverse=True))}
    for aid,(region,aum,fees,count) in advisors.items():
        r=regions.setdefault(region,[0,0,Decimal(0),Decimal(0)]);r[0]+=1;r[1]+=count;r[2]+=aum;r[3]+=fees
    return {'performance':[[pf,s[6],s[7],s[6]-s[7],s[3]/(s[6]+s[7])*10000] for pf,s in sorted(summaries.items())], 'advisor_leaderboard':[[aid,s[0],s[1],s[2],s[3],ranks[s[1]]] for aid,s in sorted(advisors.items())], 'regions':[[region,*s] for region,s in sorted(regions.items())], 'raw_trades':len(raw),'valid_trades':len(valid),'conformed_dimensions':{n:len(d) for n,d in dims.items()},'positions':len(positions),'portfolios_with_trades':len(summaries),'portfolios_without_trades':len(dims['portfolios'])-len(summaries),'total_aum':sum(s[2] for s in summaries.values()),'total_fees':sum(s[3] for s in summaries.values()),'summary':[[p,*s[:6]] for p,s in sorted(summaries.items())]}
def configuration():
    aliases={'DATABRICKS_HOST':['DBT_HOST'],'DATABRICKS_HTTP_PATH':['DBT_HTTP_PATH'],'DBT_CATALOG':['DATABRICKS_CATALOG'],'DBT_SCHEMA':['DATABRICKS_SCHEMA','V2_DB_SCHEMA']}
    for key,other in aliases.items():
        values=[os.environ[n] for n in [key,*other] if os.environ.get(n)]
        normalized=[v.removeprefix('https://').removeprefix('http://').rstrip('/') if key.endswith('HOST') else v for v in values]
        assert normalized and len(set(normalized))==1,'Missing/conflicting connection alias: '+key
        os.environ[key]=normalized[0]
    if not os.environ.get('DBT_ACCESS_TOKEN'):os.environ['DBT_ACCESS_TOKEN']=os.environ.get('DATABRICKS_TOKEN','')
    assert os.environ['DBT_ACCESS_TOKEN'],'Use the delivered OAuth setup/token refresh before execution'
    prefix=os.environ.get('DC_RELATION_PREFIX','');assert re.fullmatch(r'dc_[a-z][a-z0-9_]{2,48}',prefix),'Set a unique DC_RELATION_PREFIX, e.g. dc_alex_a01'
    for key in ['DBT_CATALOG','DBT_SCHEMA']:assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',os.environ[key]),'Invalid assigned namespace'
    return {k:os.environ[k] for k in ['DATABRICKS_HOST','DATABRICKS_HTTP_PATH','DBT_CATALOG','DBT_SCHEMA','DC_RELATION_PREFIX']}
def versions():
    import importlib.metadata as md
    result={'python':sys.version.split()[0]}
    for name in ['dbt-core','dbt-databricks','apache-airflow','astronomer-cosmos','databricks-sql-connector']:
        try:result[name]=md.version(name)
        except md.PackageNotFoundError:result[name]='not installed at this boundary'
    return result
def query(sql):
    cfg=configuration()
    from databricks import sql as connector
    with connector.connect(server_hostname=cfg['DATABRICKS_HOST'],http_path=cfg['DATABRICKS_HTTP_PATH'],access_token=os.environ['DBT_ACCESS_TOKEN'],catalog=cfg['DBT_CATALOG'],schema=cfg['DBT_SCHEMA']) as conn:
        with conn.cursor() as cur:cur.execute(sql);return [list(r) for r in cur.fetchall()]
def check(w,case):
    cfg=configuration();project=json.loads((w/'target/manifest.json').read_text());run=json.loads((w/'target/run_results.json').read_text())
    assert run['results'] and all(r['status'] in ['success','pass','warn'] for r in run['results']),'dbt results contain failure/empty execution'
    for n in project['nodes'].values():
        if n['resource_type'] in ['model','seed','snapshot']:
            assert n['schema']==cfg['DBT_SCHEMA'] and n['database']==cfg['DBT_CATALOG'],'Namespace drift'
            assert n['alias'].startswith(cfg['DC_RELATION_PREFIX']+'_'),'Relation ownership drift'
    for n in project.get('sources',{}).values():
        assert n['schema']==cfg['DBT_SCHEMA'] and n['database']==cfg['DBT_CATALOG'] and n['identifier'].startswith(cfg['DC_RELATION_PREFIX']+'_'),'Raw source ownership drift'
    relation='fund_nav_report' if case=='portfolio' else 'rpt_portfolio_summary'
    if case=='portfolio':
        table=(cfg['DC_RELATION_PREFIX']+'_fund_nav_report');metadata=query(f"select full_data_type from `{cfg['DBT_CATALOG']}`.information_schema.columns where table_schema='{cfg['DBT_SCHEMA']}' and table_name='{table}' and column_name='exposure_gbp'")
        assert len(metadata)==1 and str(metadata[0][0]).upper().replace(' ','')=='DECIMAL(28,2)','Consumer money type must be decimal(28,2)'
    columns='fund_id,position_date,holdings,exposure_gbp,nav_per_unit' if case=='portfolio' else 'portfolio_id,client_id,advisor_id,aum,fees_paid,trades,positions'
    expected=portfolio(w/'seeds') if case=='portfolio' else atlas(w/'seeds')['summary']
    actual=query(f"select {columns} from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_{relation}` order by 1,2")
    assert len(actual)==len(expected),'Output population differs from independent CSV calculation'
    for observed,wanted in zip(actual,expected):
        for value,goal in zip(observed,wanted):
            if isinstance(goal,Decimal):assert value is not None and abs(Decimal(str(value))-goal)<Decimal('0.00001'),(value,str(goal))
            else:assert str(value)==str(goal),(value,goal)
    if case=='atlas' and any(n.get('name')=='rpt_portfolio_performance' for n in project['nodes'].values()):
        oracle=atlas(w/'seeds')
        comparisons=[('rpt_portfolio_performance','portfolio_id,buy_value,sell_value,net_flow,fee_bps_realized','performance'),('rpt_advisor_leaderboard','advisor_id,region,book_aum,fees_generated,portfolios,rank','advisor_leaderboard'),('rpt_region_report','region,advisors,portfolios,aum,fees_generated','regions')]
        for table,fields,key in comparisons:
            observed=query(f"select {fields} from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_{table}` order by 1")
            desired=oracle[key];assert len(observed)==len(desired),table+' population'
            for row,want in zip(observed,desired):
                for value,goal in zip(row,want):
                    if isinstance(goal,Decimal):assert value is not None and abs(Decimal(str(value))-goal)<Decimal('.0001'),table+' value'
                    else:assert str(value)==str(goal),table+' key'
    return {'contract_sha256':digest(BASE/'dataset-runtime-contract.json'),'boundary':'connected Databricks query; scheduled Astro identity checked separately','config':cfg,'versions':versions(),'rows_checked':len(actual),'manifest_sha256':digest(w/'target/manifest.json'),'run_results_sha256':digest(w/'target/run_results.json')}
def dbt(w,command,*args):
    configuration();exe=os.environ.get('DC_DBT_BIN','dbt')
    subprocess.run([exe,command,'--project-dir',str(w),'--profiles-dir',str(w),'--target','local','--target-path',str(w/'target'),*args],check=True,cwd=w)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['prepare','reference','static','ready','run','check','check-replay','mutate','restore','stage-astro','cleanup-sql']);ap.add_argument('workspace',type=Path);ap.add_argument('--checkpoint',choices=['foundations','quality','advanced','airflow-foundations','airflow-reliable','airflow-delivery','atlas','atlas-advanced'],default='foundations');ap.add_argument('--case',choices=['portfolio','atlas'],default='portfolio');ap.add_argument('--drill',choices=['correction','new-holding','missing-fx','fund-change']);ap.add_argument('--astro-root',type=Path);ap.add_argument('--observed-at');a=ap.parse_args();w=a.workspace.resolve()
    if a.action=='prepare':
        assert not w.exists(),'Preparation refuses an existing attempt'
        paths={'foundations':'dbt-guide/01-foundations','quality':'dbt-guide/02-trustworthy-models','advanced':'dbt-guide/03-history-and-delivery','airflow-foundations':'airflow-guide/01-foundations','airflow-reliable':'airflow-guide/02-reliable-runs','airflow-delivery':'airflow-guide/03-dbt-and-astro','atlas':'atlas','atlas-advanced':'atlas/advanced'}
        source=BASE.parent/paths[a.checkpoint]/'starter'
        if not source.is_dir():
            canonical={'foundations':'dbt/phase-one-certified','quality':'dbt/phase-two-proficient','advanced':'dbt/phase-two-proficient','airflow-foundations':'airflow/phase-one-certified','airflow-reliable':'airflow/phase-two-proficient','airflow-delivery':'airflow/phase-two-proficient','atlas':'capstone/phase-one-certified','atlas-advanced':'capstone/phase-two-proficient'}
            source=BASE.parents[1]/canonical[a.checkpoint]/'starter'
        assert source.is_dir(),'Prepare from the training root with the canonical mise task; copied runtime has no separate starter authority'
        shutil.copytree(source,w);shutil.copytree(BASE,w/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
        print('Prepared independent learner baseline:',w);return
    if a.action=='reference':
        seeds=w/'seeds' if (w/'seeds').exists() else w/'project/seeds'
        print(json.dumps(portfolio(seeds) if a.case=='portfolio' else atlas(seeds),default=str,indent=2));return
    if a.action=='static':
        for p in w.rglob('*.py'):compile(p.read_text(),str(p),'exec')
        unfinished=[str(p.relative_to(w)) for p in w.rglob('*') if p.suffix in ['.sql','.py'] and ('TODO:' in p.read_text() or 'as unfinished' in p.read_text()) and 'runtime' not in p.relative_to(w).parts]
        assert not unfinished,'Untouched/incomplete learner outcomes: '+', '.join(unfinished)
        profile = (w/'profiles.yml') if (w/'profiles.yml').exists() else w/'project/profiles.yml'
        assert 'type: databricks' in profile.read_text() and 'duckdb' not in profile.read_text()
        print('Static authoring checks pass; execution remains pending');return
    if a.action=='ready':
        cfg=configuration();print(json.dumps({'configuration':cfg,'versions':versions(),'identity':query('select current_user(),current_catalog(),current_schema()')},indent=2));dbt(w,'debug');return
    if a.action=='mutate':
        assert a.drill,'Select a bounded drill'
        name={'correction':'holdings_raw','new-holding':'holdings_raw','missing-fx':'fx_rates_raw','fund-change':'fund_master_raw'}[a.drill];p=w/'seeds'/f'{name}.csv';data=rows(p);fields=list(data[0])
        if a.drill=='correction':data[0]['mkt_val_lc']=str(Decimal(data[0]['mkt_val_lc'])+1000)
        elif a.drill=='new-holding':
            added=dict(data[0]);added.update(fund_cd='PEF-EM-GROWTH',qty='4.0000',mkt_val_lc='500.00')
            key=lambda row:(row['fund_cd'],row['pos_dt'],row['isin'])
            assert key(added) not in {key(row) for row in data},'Controlled arrival key already exists; restore before another drill'
            data.append(added)
        elif a.drill=='missing-fx':data=[r for r in data if not (r['from_ccy']=='GBP' and r['rate_dt']=='2026-05-20')]
        else:data[0]['fund_name']+=' (controlled teaching change)'
        with p.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(data)
        write(w/'variation.json',{'drill':a.drill,'file':str(p.relative_to(w)),'sha256':digest(p),'restore':'restore then dbt seed/build; snapshot history persists'});return
    if a.action=='restore':
        for p in (BASE/'fixtures'/a.case).glob('*.csv'):shutil.copy2(p,w/'seeds'/p.name)
        if a.observed_at:
            instant=datetime.fromisoformat(a.observed_at.replace('Z','+00:00'));assert instant.tzinfo,'Use an explicit timezone'
            for p in (w/'seeds').glob('*.csv'):
                data=rows(p)
                if data and '_extracted_at' in data[0]:
                    for r in data:r['_extracted_at']=instant.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    with p.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
            write(w/'preparation.json',{'sample_observation_time':instant.isoformat(),'business_dates':'unchanged: 2026-05-20 and 2026-05-21','fixture_variant':'recorded refresh of load timestamps only'})
        return
    if a.action=='stage-astro':
        cfg=configuration();assert a.astro_root and (a.astro_root/'data_products').is_dir(),'Use the actual prepared Astro project root'
        dest=a.astro_root/'data_products'/cfg['DC_RELATION_PREFIX'];assert not dest.exists(),'Never overwrite another staged project'
        shutil.copytree(w,dest,ignore=shutil.ignore_patterns('target','logs','__pycache__','.env','evidence.json'))
        # Write access is limited to this owned stage's runtime artifacts; code stays read-only to workers.
        for directory in [dest/'project/target',dest/'project/logs',dest/'evidence']:
            directory.mkdir(parents=True,exist_ok=True);directory.chmod(0o777)
        write(dest/'ownership.json',{'prefix':cfg['DC_RELATION_PREFIX'],'config':cfg,'source_workspace':str(w),'contract_sha256':digest(BASE/'dataset-runtime-contract.json')});print(dest);return
    if a.action=='cleanup-sql':
        cfg=configuration();manifest=json.loads((w/'target/manifest.json').read_text());statements=[]
        for n in manifest['nodes'].values():
            if n['resource_type'] not in ['model','seed','snapshot']:continue
            assert n['database']==cfg['DBT_CATALOG'] and n['schema']==cfg['DBT_SCHEMA'] and n['alias'].startswith(cfg['DC_RELATION_PREFIX']+'_'),'Refuse unowned cleanup'
            kind='VIEW' if n.get('config',{}).get('materialized')=='view' else 'TABLE'
            statements.append(f"DROP {kind} IF EXISTS `{n['database']}`.`{n['schema']}`.`{n['alias']}`;")
        print('\n'.join(sorted(set(statements))));return
    if a.action=='check-replay':
        cfg=configuration();expected=[]
        fx={(r['from_ccy'],r['rate_dt']):Decimal(r['rate']) for r in rows(w/'seeds/fx_rates_raw.csv') if r['to_ccy']=='GBP'}
        for r in rows(w/'seeds/holdings_raw.csv'):
            expected.append([r['fund_cd'],r['pos_dt'],r['isin'],Decimal(r['mkt_val_lc'])*fx[(r['ccy_cd'],r['pos_dt'])]])
        expected.sort();actual=query(f"select fund_id,position_date,instrument_id,exposure_gbp from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_holdings_replay` order by 1,2,3")
        assert len(actual)==len(expected),'Replay lost/duplicated business keys'
        for row,want in zip(actual,expected):
            assert [str(v) for v in row[:3]]==want[:3] and abs(Decimal(str(row[3]))-want[3])<Decimal('.00001'),'Replay key/value differs from independent input'
        write(w/'replay-evidence.json',{'contract_sha256':digest(BASE/'dataset-runtime-contract.json'),'rows_checked':len(actual),'configuration':cfg,'input_sha256':digest(w/'seeds/holdings_raw.csv'),'boundary':'actual Databricks incremental relation query'})
        print(f'PASS: {len(actual)} unique replay keys and independent input values');return
    if a.action=='run':
        write(w/'execution-start.json',{'started_at':datetime.now(timezone.utc).isoformat(),'contract_sha256':digest(BASE/'dataset-runtime-contract.json'),'versions':versions()});dbt(w,'seed','--full-refresh');dbt(w,'build')
    write(w/'evidence.json',check(w,a.case));print('Connected output verification passed')
if __name__=='__main__':
    try:main()
    except (AssertionError,KeyError,FileNotFoundError) as e:print('FAIL:',e,file=sys.stderr);sys.exit(1)
