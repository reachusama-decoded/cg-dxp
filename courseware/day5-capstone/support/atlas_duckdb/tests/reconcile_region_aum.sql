-- Capstone integration proof: the regional rollup must preserve total AUM.
-- Returns a row (test FAILS) when sum(rpt_region_report.aum) drifts from
-- sum(rpt_portfolio_summary.aum) beyond a small floating-point tolerance.
select
  region_aum,
  summary_aum,
  abs(region_aum - summary_aum) as diff
from (
  select
    (select sum(aum) from {{ ref('rpt_region_report') }}) as region_aum,
    (select sum(aum) from {{ ref('rpt_portfolio_summary') }}) as summary_aum
)
where abs(region_aum - summary_aum) > 0.01
