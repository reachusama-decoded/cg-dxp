-- Public product-grain invariant; the private checker also tests exact set/values.
{{ config(enabled=var('enable_phase_2', false), tags=['phase2']) }}
select product_id from {{ ref('rpt_cg__product_research') }}
group by product_id having count(*) != 1
