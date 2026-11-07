-- Consumer-aligned product (agg_): AUM by client segment, one row per segment. Rolls
-- rpt_portfolio_summary up to client-segment level (client/portfolio counts and total AUM).
-- Feeds the segment view and the segment-AUM reconciliation test.
select
  segment,
  count(distinct client_id) as clients,
  count(*) as portfolios,
  sum(aum) as aum
from {{ ref('rpt_portfolio_summary') }}
group by segment
