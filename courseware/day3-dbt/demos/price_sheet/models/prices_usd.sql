-- prices_usd: every price in US dollars. The table consumers read.
{{ config(materialized='table') }}

select
    p.instrument_id,
    p.price_date,
    p.native_ccy,
    p.price_native,
    case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end   as fx_rate_to_usd,
    {{ to_usd('p.price_native', 'p.native_ccy', 'f.fx_rate') }}  as price_usd
from {{ ref('stg_prices') }} p
left join {{ ref('stg_fx_rates') }} f
    on  f.from_ccy  = p.native_ccy
    and f.rate_date = p.price_date
