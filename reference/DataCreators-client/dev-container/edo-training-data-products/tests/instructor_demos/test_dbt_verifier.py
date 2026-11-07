"""Real tool acceptance of consequential verifier blind spots, when prepared."""
import os,shutil,subprocess,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
pytestmark=pytest.mark.skipif(not os.environ.get('V2_DBT_BIN'),reason='Separate pinned dbt runtime required')

def verify(path):
    return subprocess.run([sys.executable,str(ROOT/'scripts/challenge-v2.py'),'verify','dbt','phase-one-certified','--workspace',str(path),'--mode','offline'],capture_output=True,text=True,timeout=180)

def copy_solution(tmp_path):
    target=tmp_path/'attempt with spaces';shutil.copytree(ROOT/'challenges/v2-solutions/dbt/phase-one-certified/solution',target);return target

def test_missing_structural_tests_are_rejected(tmp_path):
    w=copy_solution(tmp_path);(w/'models/schema.yml').unlink();p=verify(w)
    assert p.returncode==1 and 'Missing unique test' in p.stdout,p.stdout+p.stderr

def test_hard_coded_happy_path_mart_is_rejected(tmp_path):
    w=copy_solution(tmp_path)
    (w/'models/fund_exposure.sql').write_text("select 'A' as fund_id, 2 as holdings, cast(150 as decimal(18,2)) as exposure union all select 'B',2,100 union all select 'C',1,0\n")
    p=verify(w)
    assert p.returncode==1,p.stdout+p.stderr
    assert '160.00' in p.stdout or '150.00' in p.stdout

def test_equivalent_alternative_aggregation_is_accepted(tmp_path):
    w=copy_solution(tmp_path)
    (w/'models/fund_exposure.sql').write_text("with by_fund as (select fund_id,count(instrument_id) as holdings,sum(market_value) as exposure from {{ ref('stg_holdings') }} group by fund_id) select f.fund_id,f.fund_name,coalesce(h.holdings,0) as holdings,coalesce(h.exposure,0) as exposure from {{ ref('stg_funds') }} f left join by_fund h using(fund_id)\n")
    p=verify(w)
    assert p.returncode==0,p.stdout+p.stderr
    assert 'input_sensitivity' in p.stdout
