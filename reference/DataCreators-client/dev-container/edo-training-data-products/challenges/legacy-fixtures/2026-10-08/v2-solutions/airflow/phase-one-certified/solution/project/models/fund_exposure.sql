select f.fund_id, f.fund_name, count(h.instrument_id) as holdings, coalesce(sum(h.market_value),0) as exposure
from {{ ref('stg_funds') }} f left join {{ ref('stg_holdings') }} h using(fund_id)
group by f.fund_id, f.fund_name
