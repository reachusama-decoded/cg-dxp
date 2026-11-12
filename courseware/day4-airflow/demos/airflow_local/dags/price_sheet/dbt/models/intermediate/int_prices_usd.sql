-- int_prices_usd: every price joined to its day's FX rate and converted. Same rows as stg_prices.
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
