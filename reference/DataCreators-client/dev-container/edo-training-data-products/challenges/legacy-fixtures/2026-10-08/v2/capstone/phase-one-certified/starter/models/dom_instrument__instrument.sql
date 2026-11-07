select * from {{ ref('instruments') }} where instrument_id>0
