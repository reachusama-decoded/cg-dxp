-- stg_positions: cast + clean of the cash/accrued feed, deduped to the latest
-- extract per (fund, day, currency). The dedup keeps staging 1:1 on its real grain when a
-- source re-delivers the same day.
with src as (
    select * from {{ source('custodian', 'positions_raw') }}
),

deduped as (
    select
        trim(upper(fund_cd))                     as fund_id,
        cast(pos_dt as date)                     as position_date,
        upper(ccy_cd)                            as local_ccy,
        cast(cash_balance as decimal(18, 2))     as cash_balance,
        cast(accrued_interest as decimal(18, 2)) as accrued_interest,
        _extracted_at                            as _src_loaded_at,
        row_number() over (
            partition by fund_cd, pos_dt, ccy_cd
            order by _extracted_at desc
        ) as rn
    from src
)

select
    fund_id, position_date, local_ccy,
    cash_balance, accrued_interest, _src_loaded_at
from deduped
where rn = 1
