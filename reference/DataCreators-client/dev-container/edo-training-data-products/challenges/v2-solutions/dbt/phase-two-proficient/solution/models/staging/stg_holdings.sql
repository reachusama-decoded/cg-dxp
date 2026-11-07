-- stg_holdings: cast + clean only, no joins.
-- Grain matches the source: one row per (fund, position_date, isin).
with src as (
    select * from {{ source('custodian', 'holdings_raw') }}
),

renamed as (
    select
        trim(upper(fund_cd))                       as fund_id,
        cast(pos_dt as date)                       as position_date,
        isin   as instrument_id,
        cast(qty as decimal(18, 4))                as quantity,
        cast(mkt_val_lc as decimal(18, 2))         as mv_local_ccy,
        upper(ccy_cd)                              as local_ccy,
        _extracted_at                              as _src_loaded_at
    from src
    where fund_cd is not null
      and pos_dt  is not null
)

select * from renamed
