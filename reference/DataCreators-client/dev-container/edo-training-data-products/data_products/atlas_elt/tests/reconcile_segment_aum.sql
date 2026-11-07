-- Reconciliation: the per-segment rollup must preserve total AUM.
-- Every portfolio belongs to exactly one client segment, so sum(aum) across
-- segments must equal sum(aum) across portfolios. Returns a row (test FAILS)
-- only when the two totals drift beyond a small floating-point tolerance.
select
  segment_total,
  summary_total,
  abs(segment_total - summary_total) as diff
from (
  select
    (select sum(aum) from {{ ref('agg_segment_aum') }}) as segment_total,
    (select sum(aum) from {{ ref('rpt_portfolio_summary') }}) as summary_total
)
where abs(segment_total - summary_total) > 0.01
