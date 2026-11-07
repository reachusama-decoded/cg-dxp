-- agg_fund_daily_exposure: per-(fund, date) total base-ccy exposure, rolled up
-- from agg_fund_exposure (one grain coarser — across all strategies).
with strat as (
    select * from {{ ref('agg_fund_exposure') }}
)

select
    fund_id,
    position_date,
    sum(exposure_base_ccy)      as total_exposure_base_ccy,
    sum(cash_exposure_base_ccy) as total_cash_base_ccy
from strat
group by 1, 2
