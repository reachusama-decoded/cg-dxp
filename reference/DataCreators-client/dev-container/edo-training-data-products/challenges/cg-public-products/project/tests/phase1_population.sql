-- Public invariant, not private solution verification: missing/extra/duplicate ETF keys fail.
{{ config(enabled=var('enable_phase_1', false), tags=['phase1']) }}
with expected as (
 select distinct product_id from {{ ref('cg_products') }}
 where source_area='etfs' and source_layer='detail_page'
), actual as (select product_id from {{ ref('dom_cg__product_cost') }})
select 'missing_key' as reason, product_id from expected
where product_id not in (select product_id from actual)
union all
select 'extra_key', product_id from actual
where product_id not in (select product_id from expected)
union all
select 'duplicate_key', product_id from actual group by product_id having count(*) != 1
