-- Reconciliation: rolling the strategy-level exposure up to (fund, date) must
-- preserve the total. Returns a row (test FAILS) only when the daily total drifts
-- from the strategy-level total beyond a small floating-point tolerance.
select
    daily_total,
    strat_total,
    abs(daily_total - strat_total) as diff
from (
    select
        (select sum(total_exposure_base_ccy) from {{ ref('agg_fund_daily_exposure') }}) as daily_total,
        (select sum(exposure_base_ccy)       from {{ ref('agg_fund_exposure') }})       as strat_total
)
where abs(daily_total - strat_total) > 0.01
