-- AUTHOR: a second call site with different column names proves macro generality.
select enquiry_id, cast(null as decimal(12,4)) as training_fee_bps
from {{ ref('cg_training_enquiries') }} where 1=0
