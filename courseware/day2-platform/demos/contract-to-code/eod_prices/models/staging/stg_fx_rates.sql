-- Only USD-base rates are relevant to this product (contract: prices reported in USD).
select
    upper(from_ccy)                as from_ccy,
    upper(to_ccy)                  as to_ccy,
    cast(rate_dt as date)          as rate_date,
    cast(rate as decimal(18, 8))   as fx_rate
from {{ source('fx_feed', 'fx_rates_raw') }}
where upper(to_ccy) = 'USD'
