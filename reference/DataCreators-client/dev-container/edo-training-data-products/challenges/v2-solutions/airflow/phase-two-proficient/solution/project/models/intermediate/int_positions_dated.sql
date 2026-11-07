-- int_positions_dated: cash + accrued rolled into one figure per (fund, day).
with positions as (
    select * from {{ ref('stg_positions') }}
)

select
    fund_id,
    position_date,
    local_ccy,
    cash_balance + accrued_interest as cash_plus_accrued
from positions
