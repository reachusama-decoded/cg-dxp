-- Consumer-aligned: the US price sheet. Contract scope: active, US-listed instruments,
-- one row per instrument per business date, prices in USD, delivered by 07:30 ET.
select
    instrument_id || '|' || cast(price_date as varchar)  as price_key,
    instrument_id,
    ticker,
    instrument_name,
    price_date,
    price_native,
    native_ccy,
    fx_rate_to_usd,
    price_usd,
    price_source,
    vendor_ts
from {{ ref('int_prices_usd') }}
where market = 'US'
  and is_active
