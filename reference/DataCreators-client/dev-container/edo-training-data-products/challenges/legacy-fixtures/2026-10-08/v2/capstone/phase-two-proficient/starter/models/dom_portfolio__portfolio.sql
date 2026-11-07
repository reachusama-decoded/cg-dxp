select * from {{ ref('portfolios') }} where portfolio_id>0
