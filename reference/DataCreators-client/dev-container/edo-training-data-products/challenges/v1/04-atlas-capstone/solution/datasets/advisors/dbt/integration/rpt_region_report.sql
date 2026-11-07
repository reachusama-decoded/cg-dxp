-- Consumer-aligned product (rpt_): regional rollup of the advisor book, one row per advisor
-- region. Built from rpt_portfolio_summary (which carries the advisor region per portfolio),
-- so sum(aum) here reconciles to sum(aum) in rpt_portfolio_summary
-- (see tests/reconcile_region_aum.sql).
select
  region,
  count(*) as portfolios,
  count(distinct client_id) as clients,
  sum(aum) as aum,
  sum(fees_paid) as fees_generated
from {{ ref('rpt_portfolio_summary') }}
group by region
