-- Consumer-aligned product (rpt_): the advisor leaderboard, one row per advisor. Reads
-- rpt_advisor_book and adds a ranking. Read by the advisor dashboard.
-- Advisors ranked by book AUM. dense_rank() so ties share a rank with no gaps.
select
  advisor_id,
  advisor_name,
  region,
  portfolios,
  book_aum,
  fees_generated,
  dense_rank() over (order by book_aum desc) as rank
from {{ ref('rpt_advisor_book') }}
