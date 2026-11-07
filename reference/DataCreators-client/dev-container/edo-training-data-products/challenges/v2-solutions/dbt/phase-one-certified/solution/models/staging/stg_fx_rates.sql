-- stg_fx_rates: cast + clean of the FX feed, narrowed to GBP-base rates.
with src as (
    select * from {{ source('fx_feed', 'fx_rates_raw') }}
)

select
    upper(from_ccy)                       as from_ccy,
    upper(to_ccy)                         as to_ccy,
    cast(rate_dt as date)                 as rate_date,
    cast(rate as decimal(18, 8))          as fx_rate
from src
where upper(to_ccy) = 'GBP'
