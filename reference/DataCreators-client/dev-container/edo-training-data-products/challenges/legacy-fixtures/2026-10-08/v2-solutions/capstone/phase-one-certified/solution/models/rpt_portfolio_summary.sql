-- Consumer-aligned product (rpt_): the executive portfolio rollup, one row per portfolio.
-- Aggregates the canonical position and joins the portfolio/party dimensions to give AUM,
-- fees paid, trade count, and position count per portfolio. The hub report the advisor-book,
-- segment-AUM, and region rollups (and their reconciliations) build on.
select
  pf.portfolio_id,
  pf.strategy,
  c.client_id,
  c.name as client_name,
  c.segment,
  a.advisor_id,
  a.name as advisor_name,
  a.region,
  count(*) as positions,
  sum(g.market_value) as aum,
  sum(g.fees) as fees_paid,
  sum(g.trades) as trades
from {{ ref('dom_positions__position') }} g
join {{ ref('dom_portfolio__portfolio') }} pf using (portfolio_id)
join {{ ref('dom_party__client') }} c using (client_id)
join {{ ref('dom_party__advisor') }} a using (advisor_id)
group by
  pf.portfolio_id,
  pf.strategy,
  c.client_id,
  c.name,
  c.segment,
  a.advisor_id,
  a.name,
  a.region
