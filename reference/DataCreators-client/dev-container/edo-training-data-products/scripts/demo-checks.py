#!/usr/bin/env python3
"""Independent observed dbt outcomes, computed from the copied CSV inputs."""
import argparse,csv,json
from decimal import Decimal
from pathlib import Path
import duckdb

def exposure(root):
    holdings=list(csv.DictReader((root/'seeds/holdings.csv').open()))
    funds=list(csv.DictReader((root/'seeds/funds.csv').open()))
    assert len({r['fund_id'] for r in funds})==len(funds),'Duplicate fund keys'
    keys={(r['fund_id'],r['instrument_id']) for r in holdings}
    assert len(keys)==len(holdings),'Duplicate holding grain'
    assert {r['fund_id'] for r in holdings}<={r['fund_id'] for r in funds},'Unmatched fund key'
    expected={r['fund_id']:[0,Decimal(0)] for r in funds}
    for r in holdings:
        expected[r['fund_id']][0]+=1;expected[r['fund_id']][1]+=Decimal(r['market_value'])
    with duckdb.connect(str(root/'training.duckdb'),read_only=True) as c:
        rows=c.execute('select fund_id,holdings,exposure from fund_exposure order by fund_id').fetchall()
        actual={f:[count,Decimal(str(value))] for f,count,value in rows}
        assert len(rows)==len(expected) and actual==expected,(actual,expected)
        stage=c.execute('select fund_id,instrument_id,market_value from stg_holdings').fetchall()
        assert {(f,i,Decimal(str(v))) for f,i,v in stage}=={(r['fund_id'],r['instrument_id'],Decimal(r['market_value'])) for r in holdings}
        data_type=c.execute("select data_type from information_schema.columns where table_name='stg_holdings' and column_name='market_value'").fetchone()[0]
        assert data_type=='DECIMAL(18,2)',data_type
    print('CSV/Decimal independent per-fund calculation')
    print('fund   holdings   exposure')
    for f,(n,v) in actual.items():print(f'{f:<6} {n:<10} {v}')
    print(f'Input: {len(holdings)} holdings; total: {sum(v[1] for v in expected.values())}')

def relationship_failure(root):
    results=json.loads((root/'target/run_results.json').read_text())['results']
    failed=[r['unique_id'] for r in results if r['status']=='fail']
    assert any('relationships_stg_holdings' in r for r in failed),failed
    assert any(r['unique_id'].endswith('.fund_exposure') and r['status']=='skipped' for r in results),results
    with duckdb.connect(str(root/'training.duckdb'),read_only=True) as c:
        assert c.execute("select count(*) from information_schema.tables where table_name='fund_exposure'").fetchone()[0]==0,'Stale or incorrectly published mart'
    print(json.dumps({'failed_tests':failed,'publication':'fund_exposure skipped and relation absent'}))

def lineage(root):
    m=json.loads((root/'target/manifest.json').read_text())
    nodes=m['nodes'];mart=next(v for v in nodes.values() if v['resource_type']=='model' and v['name']=='fund_exposure')
    assert {x.split('.')[-1] for x in mart['depends_on']['nodes']}=={'stg_funds','stg_holdings'}
    for name,source in [('stg_funds','funds'),('stg_holdings','holdings')]:
        n=next(v for v in nodes.values() if v['resource_type']=='model' and v['name']==name)
        assert any(x.startswith('source.') and x.endswith('.training.'+source) for x in n['depends_on']['nodes'])
    print('Observed lineage: sources → typed staging → fund_exposure')

def fanout_failure(root):
    holdings=list(csv.DictReader((root/'seeds/holdings.csv').open()))
    labels=list(csv.DictReader((root/'fixtures/fund_labels_duplicate.csv').open()))
    expected=sum(Decimal(r['market_value']) for r in holdings for label in labels if label['fund_id']==r['fund_id'])
    with duckdb.connect(str(root/'training.duckdb'),read_only=True) as c:
        rows,total=c.execute('select sum(holdings),sum(exposure) from fund_exposure').fetchone()
    assert rows==7 and Decimal(str(total))==expected==Decimal(400),(rows,total,expected)
    failed=json.loads((root/'target/run_results.json').read_text())['results']
    assert any(r['status']=='fail' and r['unique_id'].endswith('.reconcile_exposure') for r in failed),failed
    print('Observed fan-out: 7 joined holdings, exposure 400; reconciliation failed')

def arrival_ledger(root):
    seeds=list(csv.DictReader((root/'seeds/arrivals.csv').open()))
    expected={r['event_id']:(r['fund_id'],Decimal(r['market_value'])) for r in seeds}
    assert len(expected)==len(seeds),'Duplicate input event identities'
    with duckdb.connect(str(root/'training.duckdb'),read_only=True) as c:
        rows=c.execute('select event_id,fund_id,market_value from arrival_ledger order by event_id').fetchall()
    assert len(rows)==len(expected) and {e:(f,Decimal(str(v))) for e,f,v in rows}==expected,'Incremental event/value mismatch'
    print('Independent event oracle: '+str(len(rows))+' identities, total '+str(sum(v[1] for v in expected.values())))

if __name__=='__main__':
    checks={'exposure':exposure,'relationship-failure':relationship_failure,'lineage':lineage,'fanout-failure':fanout_failure,'arrival-ledger':arrival_ledger}
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('check',choices=list(checks));ap.add_argument('--workspace',type=Path,default=Path.cwd());a=ap.parse_args()
    checks[a.check](a.workspace)
