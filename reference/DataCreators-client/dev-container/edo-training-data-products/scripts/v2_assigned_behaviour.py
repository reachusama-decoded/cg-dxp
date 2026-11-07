"""Prepared live behavioral drills; no offline result can establish these gates."""
import csv,importlib.util,json,pathlib,subprocess,sys
from decimal import Decimal

def verify(workspace,tool,phase):
    w=pathlib.Path(workspace)
    spec=importlib.util.spec_from_file_location('assigned_behaviour_lab',w/'runtime/lab.py')
    lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
    project=w/'project' if (w/'project').is_dir() else w
    cfg=lab.configuration();evidence={};saved_region=None
    def query(relation,projection,where=''):
        return lab.query(f"select {projection} from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_{relation}` {where}")
    def action(name,*args):
        subprocess.run([sys.executable,str(w/'runtime/lab.py'),name,str(project),*args],check=True,capture_output=True,text=True)
    def restore():
        action('restore','--case','atlas' if tool=='capstone' else 'portfolio')
        lab.dbt(project,'seed','--full-refresh');lab.dbt(project,'build');lab.check(project,'atlas' if tool=='capstone' else 'portfolio')
    def write_csv(path,rows):
        with path.open('w',newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    def failed_test(select,expected_names):
        lab.dbt(project,'test','--select',select,expected=1)
        run=json.loads((project/'target/run_results.json').read_text());manifest=json.loads((project/'target/manifest.json').read_text())
        names=[manifest['nodes'][r['unique_id']]['name'] for r in run['results'] if r['status']=='fail']
        assert any(any(expected in name for expected in expected_names) for name in names),'Negative case failed for the wrong reason'
        return names
    try:
        if tool=='dbt':
            prefix=cfg['DC_RELATION_PREFIX']
            types=lab.query(f"select table_name,table_type from `{cfg['DBT_CATALOG']}`.information_schema.tables where table_schema='{cfg['DBT_SCHEMA']}' and table_name in ('{prefix}_stg_holdings','{prefix}_fund_nav_report')")
            kinds=dict(types);assert kinds[prefix+'_stg_holdings']=='VIEW' and kinds[prefix+'_fund_nav_report']!='VIEW','Materialization contract differs'
            evidence['materializations']=kinds
            if phase=='phase-one-certified':
                path=project/'seeds/holdings_raw.csv';rows=lab.rows(path);original=path.read_text();rows[0]['mkt_val_lc']='0';key=(rows[0]['fund_cd'],rows[0]['pos_dt'],rows[0]['isin'])
                write_csv(path,rows);lab.dbt(project,'seed','--select','holdings_raw');lab.dbt(project,'build','--select','stg_holdings')
                staged=query('stg_holdings','fund_id,position_date,instrument_id,mv_local_ccy')
                assert len(staged)==8 and len({tuple(str(v) for v in row[:3]) for row in staged})==8
                assert any(tuple(str(v) for v in row[:3])==key and Decimal(str(row[3]))==0 for row in staged),'Zero-valued holding key was lost'
                evidence['zero_value_retains_key']=list(key)
                path.write_text(original);rows=lab.rows(path);rows[0]['fund_cd']='UNKNOWN';write_csv(path,rows)
                lab.dbt(project,'seed','--select','holdings_raw');lab.dbt(project,'run','--select','stg_holdings')
                evidence['unknown_fund_failure']=failed_test('matched_funds test_type:generic',['matched_funds','relationships'])
                restore();evidence['restored_independent_output']=lab.check(project,'portfolio')
            else:
                action('mutate','--drill','missing-fx');lab.dbt(project,'seed','--select','fx_rates_raw');lab.dbt(project,'run','--select','int_holdings_enriched')
                evidence['missing_fx_failure']=failed_test('matched_enrichment',['matched_enrichment']);restore()
                action('mutate','--drill','correction');lab.dbt(project,'seed','--select','holdings_raw')
                for _ in range(2):
                    lab.dbt(project,'run','--select','holdings_replay');action('check-replay')
                evidence['correction_replay']=json.loads((project/'replay-evidence.json').read_text())
                action('mutate','--drill','new-holding');lab.dbt(project,'seed','--select','holdings_raw')
                for _ in range(2):
                    lab.dbt(project,'run','--select','holdings_replay');action('check-replay')
                evidence['insert_replay']=json.loads((project/'replay-evidence.json').read_text())
                assert evidence['insert_replay']['rows_checked']==9,'New key was not inserted exactly once'
                lab.dbt(project,'run','--select','fund_nav_report')
                evidence['baseline_nav_rejects_variant']=failed_test('nav_reconciliation',['nav_reconciliation']);restore()
                lab.dbt(project,'run','--select','holdings_replay','--full-refresh');action('check-replay')
                lab.dbt(project,'snapshot');raw=lab.rows(project/'seeds/fund_master_raw.csv');key=raw[0]['fund_cd']
                action('mutate','--drill','fund-change');lab.dbt(project,'seed','--select','fund_master_raw');lab.dbt(project,'snapshot')
                safe_key=key.replace("'","''")
                history=query('fund_history','fund_cd,fund_name,dbt_valid_from,dbt_valid_to',f"where fund_cd='{safe_key}'")
                active=[row for row in history if row[3] is None];closed=[row for row in history if row[3] is not None]
                assert len(active)==1 and 'controlled teaching change' in active[0][1] and closed,'Snapshot did not retain closed/current versions'
                assert all(row[2]<row[3] for row in closed),'Invalid snapshot interval'
                evidence['snapshot_changed_key']=history;restore()
        elif phase=='phase-one-certified':
            counts={name:query(name,'count(*)')[0][0] for name in ['trades','dom_trading__trade','dom_positions__position','dom_portfolio__portfolio']}
            assert counts=={'trades':10000,'dom_trading__trade':9880,'dom_positions__position':3717,'dom_portfolio__portfolio':2500},counts
            evidence['actual_populations']=counts
            bad=lab.query(f"select count(*) from `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_dom_portfolio__portfolio` p join `{cfg['DBT_CATALOG']}`.`{cfg['DBT_SCHEMA']}`.`{cfg['DC_RELATION_PREFIX']}_dom_party__advisor` a on p.client_id=a.advisor_id")[0][0]
            assert bad<2500; evidence['wrong_key_diagnostic_count']=bad
            path=project/'seeds/trades.csv';rows=lab.rows(path);row=next(r for r in rows if Decimal(r['qty'])>0 and Decimal(r['price_cents'])>0 and r['side'] in ['B','S']);row['side']='X';write_csv(path,rows)
            lab.dbt(project,'seed','--select','trades');lab.dbt(project,'run')
            assert query('dom_trading__trade','count(*)')==[[9879]],'Controlled invalid side was not filtered'
            evidence['input_sensitivity_output']=lab.check(project,'atlas');restore()
        else:
            assert sorted(lab.query('select dense_rank() over(order by v desc) from (values(10),(10),(5)) t(v)'))==[[1],[1],[2]]
            assert lab.query('select 1.0/nullif(0,0)')==[[None]]
            evidence['explicit_tie_and_zero_cases']='dense ranks 1/1/2; zero denominator NULL'
            advisor=int(query('rpt_advisor_leaderboard','advisor_id','order by advisor_id limit 1')[0][0]);path=project/'models/rpt_region_report.sql';original=path.read_text();saved_region=(path,original)
            path.write_text("select region,count(*) as advisors,sum(portfolios) as portfolios,sum(book_aum) as aum,sum(fees_generated) as fees_generated from {{ ref('rpt_advisor_leaderboard') }} where advisor_id <> "+str(advisor)+' group by region\n')
            lab.dbt(project,'run','--select','rpt_region_report');evidence['omitted_region_failure']=failed_test('reconcile_region',['reconcile_region'])
            path.write_text(original);lab.dbt(project,'build');evidence['repaired_independent_output']=lab.check(project,'atlas')
    finally:
        # Only copied fixtures and this explicitly owned namespace are restored.
        # Current captured history is not dropped; source bytes stay untouched.
        if saved_region:saved_region[0].write_text(saved_region[1])
        restore()
        if tool=='dbt' and phase=='phase-two-proficient':
            lab.dbt(project,'run','--select','holdings_replay','--full-refresh');action('check-replay')
    return evidence
