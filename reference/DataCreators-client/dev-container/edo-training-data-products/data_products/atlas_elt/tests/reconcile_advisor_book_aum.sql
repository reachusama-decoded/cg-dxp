-- Reconciliation: the per-advisor rollup must preserve total AUM.
-- Every portfolio has exactly one advisor, so sum(book_aum) across advisors must
-- equal sum(aum) across portfolios. Returns a row (test FAILS) only when the two
-- totals drift beyond a small floating-point tolerance.
select
  book_total,
  summary_total,
  abs(book_total - summary_total) as diff
from (
  select
    (select sum(book_aum) from {{ ref('rpt_advisor_book') }}) as book_total,
    (select sum(aum) from {{ ref('rpt_portfolio_summary') }}) as summary_total
)
where abs(book_total - summary_total) > 0.01
