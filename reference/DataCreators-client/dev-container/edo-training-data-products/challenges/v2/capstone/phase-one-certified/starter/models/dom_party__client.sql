select * from {{ ref('clients') }} where client_id>0
