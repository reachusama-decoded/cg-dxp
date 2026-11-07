-- agg_fund_exposure: per-fund per-day exposure aggregate by strategy.
-- Used by compliance for concentration alerts. `agg_` is the prefix for a
-- pre-computed measure grouped by reporting dimensions.
with holdings as (
    select * from {{ ref('int_holdings_enriched') }}
),

funds as (
    select * from {{ ref('int_fund_attributes') }}
)

select
    h.fund_id,
    h.position_date,
    f.strategy_code,
    sum(h.mv_base_ccy)                                    as exposure_base_ccy,
    count(distinct h.instrument_id)                       as instrument_count,
    sum(case when h.instrument_id like 'CASH_%'
             then h.mv_base_ccy else 0 end)               as cash_exposure_base_ccy
from holdings h
left join funds f
    on f.fund_id = h.fund_id
group by 1, 2, 3
