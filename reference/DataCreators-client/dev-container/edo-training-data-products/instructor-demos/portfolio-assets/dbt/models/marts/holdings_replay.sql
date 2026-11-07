{{ config(materialized='incremental', incremental_strategy='merge', unique_key=['fund_id','position_date','instrument_id']) }}
-- Read all eight fixture rows on every run to catch corrections, not only newer dates.
select fund_id, position_date, instrument_id, {{ native_value('mv_local_ccy','fx_rate_to_base') }} as exposure_gbp
from {{ ref('int_holdings_enriched') }}
