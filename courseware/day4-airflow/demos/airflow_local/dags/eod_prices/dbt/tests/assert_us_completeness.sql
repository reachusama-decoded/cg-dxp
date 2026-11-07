-- Contract SLA: on the latest priced date, at least 99.5% of active US instruments must
-- have a price. Returns a row (FAIL) when coverage is below that.
with active_us as (
    select count(*) as expected from {{ ref('stg_instruments') }} where market = 'US' and is_active
),
latest as (
    select max(price_date) as price_date from {{ ref('rpt_eod_prices_us') }}
),
priced as (
    select count(*) as actual from {{ ref('rpt_eod_prices_us') }} where price_date = (select price_date from latest)
)
select actual, expected, actual * 1.0 / expected as coverage
from priced, active_us
where actual * 1.0 / expected < 0.995
