-- Stretch: the same (fund, date) rollup as agg_fund_daily_exposure, built incrementally.
-- First run: full load. Later runs: only dates after the latest already in the table,
-- replaced with delete+insert on the unique key so a re-delivered day is idempotent.
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['fund_id', 'position_date']
) }}

with holdings as (
    select * from {{ ref('int_holdings_enriched') }}
)

select
    fund_id,
    position_date,
    sum({{ to_base_ccy('mv_local_ccy', 'fx_rate_to_base') }}) as total_exposure_base_ccy,
    count(*)                                                   as positions
from holdings
{% if is_incremental() %}
where position_date > (select coalesce(max(position_date), date '1900-01-01') from {{ this }})
{% endif %}
group by 1, 2
