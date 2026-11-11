-- fct_prices_usd: the price sheet consumers read. One row per instrument per day.
select
    instrument_id,
    price_date,
    native_ccy,
    price_native,
    fx_rate_to_usd,
    price_usd
from {{ ref('int_prices_usd') }}
