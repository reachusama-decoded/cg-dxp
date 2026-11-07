-- stg_prices: cast + clean of the Bloomberg EOD prices, deduped to the latest
-- extract per (instrument, day).
with src as (
    select * from {{ source('bloomberg', 'prices_raw') }}
),

latest_per_day as (
    select
        upper(isin)                            as instrument_id,
        cast(price_dt as date)                 as price_date,
        cast(close_px as decimal(18, 6))       as close_price,
        upper(quote_ccy)                       as price_ccy,
        _extracted_at                          as _src_loaded_at,
        row_number() over (
            partition by isin, price_dt
            order by _extracted_at desc
        ) as rn
    from src
)

select
    instrument_id, price_date, close_price, price_ccy, _src_loaded_at
from latest_per_day
where rn = 1
