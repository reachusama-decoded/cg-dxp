-- stg_prices: one row per raw price, renamed and typed. No joins, no business logic.
select
    upper(trim(isin))                  as instrument_id,
    cast(px_date as date)              as price_date,
    cast(px_close as decimal(18, 6))   as price_native,
    upper(trim(px_ccy))                as native_ccy,      -- the fix: 'gbp' becomes 'GBP'
    cast(vendor_ts as timestamp)       as vendor_ts
from {{ source('vendor_feed', 'vendor_prices_raw') }}
