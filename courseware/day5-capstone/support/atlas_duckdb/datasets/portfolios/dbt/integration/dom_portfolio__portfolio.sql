-- Domain-aligned product · Portfolio domain. The canonical portfolio, one row per
-- portfolio. Trims strategy, keeps the client/advisor business keys, and drops non-positive
-- ids. Conformed portfolio read by rpt_portfolio_summary and snapshotted for SCD history.
select
  portfolio_id,
  client_id,
  advisor_id,
  trim(strategy) as strategy,
  inception_date
from {{ ref('src_portfolio__portfolios') }}
where portfolio_id > 0
