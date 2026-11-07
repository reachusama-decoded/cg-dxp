select fund_id, position_date, instrument_id from {{ ref('stg_holdings') }} group by 1,2,3 having count(*) <> 1
