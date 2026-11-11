-- stg_fx_rates: one row per currency per day
select
    from_ccy,
    cast(rate_dt as date)              as rate_date,
    cast(rate as decimal(18, 6))       as fx_rate
from {{ source('fx_feed', 'fx_rates_raw') }}
