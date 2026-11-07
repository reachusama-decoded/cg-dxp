-- int_fund_attributes: the active funds with their reporting attributes.
-- Filters to is_active so downstream marts only carry live funds.
with funds as (
    select * from {{ ref('stg_funds') }}
)

select
    fund_id,
    fund_name,
    inception_date,
    base_ccy,
    strategy_code
from funds
where is_active = true
