-- Lookup + derive: instrument attributes by instrument_id, FX by (currency, date);
-- price_usd = price_native x rate, with USD a constant rate of 1. A non-USD price with no
-- rate for that date stays NULL so the mart's not_null test catches it (no silent 1.0).
with prices as (
    select * from {{ ref('stg_vendor_prices') }}
),

instruments as (
    select * from {{ ref('stg_instruments') }}
),

fx as (
    select * from {{ ref('stg_fx_rates') }}
)

select
    p.instrument_id,
    i.ticker,
    i.instrument_name,
    i.market,
    i.is_active,
    p.price_date,
    p.price_native,
    p.native_ccy,
    case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end     as fx_rate_to_usd,
    cast(cast(p.price_native as decimal(19, 6))
         * case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end
         as decimal(18, 6))                                        as price_usd,
    p.vendor_ts,
    'VENDOR'                                                        as price_source
from prices p
left join instruments i
    on i.instrument_id = p.instrument_id
left join fx f
    on f.from_ccy = p.native_ccy
    and f.rate_date = p.price_date
