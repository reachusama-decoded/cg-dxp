-- AUTHOR: retain every enquiry, derive a two-clock as-of join, expose no-match/ambiguity.
select e.enquiry_id, e.product_id, e.business_date, e.knowledge_cutoff,
       cast(null as decimal(12,4)) as training_fee_bps, cast(null as string) as history_row_uid
from {{ ref('cg_training_enquiries') }} e where 1=0
