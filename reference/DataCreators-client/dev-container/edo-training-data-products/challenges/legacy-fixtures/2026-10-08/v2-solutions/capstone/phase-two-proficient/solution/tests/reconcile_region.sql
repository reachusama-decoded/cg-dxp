select 1 as failure where abs((select sum(aum) from {{ ref('rpt_region_report') }}) - (select sum(aum) from {{ ref('rpt_portfolio_summary') }})) > 0.01
