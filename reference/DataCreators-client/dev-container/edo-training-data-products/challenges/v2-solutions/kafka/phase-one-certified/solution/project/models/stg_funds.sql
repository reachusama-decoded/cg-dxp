select fund_id, fund_name from {{ source('training', 'funds') }}
