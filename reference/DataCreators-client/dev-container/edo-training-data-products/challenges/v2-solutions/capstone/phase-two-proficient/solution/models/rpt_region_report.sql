select region, count(*) as advisors, sum(portfolios) as portfolios, sum(book_aum) as aum, sum(fees_generated) as fees_generated from {{ ref('rpt_advisor_leaderboard') }} group by region
