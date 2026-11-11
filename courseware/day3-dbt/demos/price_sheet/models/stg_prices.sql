-- stg_prices: one row per instrument per day, renamed and typed. No joins, no business logic.
with typed as (
    select
        upper(trim(isin))                  as instrument_id,
        cast(px_date as date)              as price_date,
        cast(px_close as decimal(18, 6))   as price_native,
        upper(trim(px_ccy))                as native_ccy,
        cast(vendor_ts as timestamp)       as vendor_ts
    from {{ source('vendor_feed', 'vendor_prices_raw') }}
),

ranked as (
    select *,
           row_number() over (partition by instrument_id, price_date order by vendor_ts desc) as rn
    from typed
)

-- the fix: when the vendor delivers a price twice, the latest delivery wins
select instrument_id, price_date, price_native, native_ccy, vendor_ts
from ranked
where rn = 1
