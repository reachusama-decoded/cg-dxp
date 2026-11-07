-- Domain-aligned product · Fund domain. The canonical fund, one row per fund. Trims text
-- and drops non-positive ids. Conformed fund read by agg_fund_nav.
select
  fund_id,
  trim(name) as name,
  trim(style) as style
from {{ ref('src_fundref__funds') }}
where fund_id > 0
