-- stg_funds: cast + clean of the fund master. One row per fund.
with src as (
    select * from {{ source('product_ref', 'fund_master_raw') }}
)

select
    trim(upper(fund_cd))                  as fund_id,
    fund_name,
    cast(inception_dt as date)            as inception_date,
    upper(base_ccy)                       as base_ccy,
    strategy_code,
    is_active
from src
