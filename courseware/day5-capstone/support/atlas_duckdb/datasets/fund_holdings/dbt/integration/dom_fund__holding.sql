-- Domain-aligned product · Fund domain. The canonical fund holding, one row per
-- fund/instrument pair. Drops non-positive ids and zero/negative weights. Read by agg_fund_nav.
select
  fund_id,
  instrument_id,
  weight_pct
from {{ ref('src_fundref__fund_holdings') }}
where fund_id > 0
  and instrument_id > 0
  and weight_pct > 0
