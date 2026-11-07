-- int_holdings_enriched: holdings x prices x fx. This is where the joins live;
-- staging stays 1:1. Output grain is unchanged from stg_holdings:
-- (fund_id, position_date, instrument_id).
with holdings as (
    select * from {{ ref('stg_holdings') }}
),

prices as (
    select * from {{ ref('stg_prices') }}
),

fx as (
    select * from {{ ref('stg_fx_rates') }}
),


joined as (
    select
        h.fund_id,
        h.position_date,
        h.instrument_id,
        h.quantity,
        h.mv_local_ccy,
        h.local_ccy,
        p.close_price,
        f.fx_rate                                   as fx_rate_to_base,
        -- Base-currency MV: GBP funds get fx_rate = 1.0 via COALESCE.
        -- DuckDB demo copy: widened to decimal(19,2) so decimal * decimal stays in range.
        -- The learners' Databricks version reads: h.mv_local_ccy * coalesce(f.fx_rate, 1.0)
        cast(cast(h.mv_local_ccy as decimal(19, 2)) * coalesce(f.fx_rate, 1.0) as decimal(18, 2)) as mv_base_ccy
    from holdings h
    left join prices p
        on p.instrument_id = h.instrument_id
        and p.price_date = h.position_date
    left join fx f
        on f.from_ccy = h.local_ccy
        and f.to_ccy = 'GBP'
        and f.rate_date = h.position_date
)

select * from joined
