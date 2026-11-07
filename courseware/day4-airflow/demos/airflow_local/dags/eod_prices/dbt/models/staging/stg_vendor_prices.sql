-- STTM rule: one price per instrument per date; when the vendor re-delivers, the latest
-- vendor_ts wins (lookup-free dedup). Currency codes are normalised to upper case.
with src as (
    select * from {{ source('vendor_feed', 'vendor_prices_raw') }}
),

deduped as (
    select
        upper(trim(isin))                         as instrument_id,
        cast(px_date as date)                     as price_date,
        cast(px_close as decimal(18, 6))          as price_native,
        upper(trim(px_ccy))                       as native_ccy,
        cast(vendor_ts as timestamp)              as vendor_ts,
        _received_at,
        row_number() over (
            partition by upper(trim(isin)), cast(px_date as date)
            order by cast(vendor_ts as timestamp) desc
        )                                         as rn
    from src
    where isin is not null and px_date is not null
)

select instrument_id, price_date, price_native, native_ccy, vendor_ts, _received_at
from deduped
where rn = 1
