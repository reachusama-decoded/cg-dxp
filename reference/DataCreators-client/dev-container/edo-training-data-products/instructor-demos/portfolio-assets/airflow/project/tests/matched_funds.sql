select h.* from {{ ref('stg_holdings') }} h left join {{ ref('stg_funds') }} f on h.fund_id=f.fund_id where f.fund_id is null
