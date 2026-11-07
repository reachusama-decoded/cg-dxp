-- Consumer-aligned product (rpt_): the advisor "book", one row per advisor. Rolls
-- rpt_portfolio_summary up to advisor level (portfolio/client counts, book AUM, fees
-- generated). Feeds the advisor leaderboard and the advisor-book AUM reconciliation test.
select
  advisor_id,
  advisor_name,
  region,
  count(*) as portfolios,
  count(distinct client_id) as clients,
  sum(aum) as book_aum,
  sum(fees_paid) as fees_generated
from {{ ref('rpt_portfolio_summary') }}
group by advisor_id, advisor_name, region
