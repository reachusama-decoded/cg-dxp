-- Reject an input-contract violation before arbitrary deduplication can hide it.
{{ config(enabled=var('enable_phase_1', false), tags=['phase1']) }}
with p as (
 select product_id from {{ ref('cg_products') }}
 where source_area='etfs' and source_layer='detail_page'
)
select p.product_id
from p left join {{ ref('cg_fees') }} f
 on p.product_id=f.product_id and f.source_layer='detail_page'
 and f.source_area='etfs' and f.component='net_expense_ratio'
group by p.product_id having count(f.product_id) != 1
