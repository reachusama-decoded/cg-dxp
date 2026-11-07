-- Reporting currency is GBP, including funds whose master base_ccy is USD.
-- Cash is separately dated/converted, and is excluded from the supplied NAV numerator.
select h.fund_id, h.position_date, count(*) as holdings,
       cast(sum(h.mv_base_ccy) as decimal(28,2)) as exposure_gbp,
       cast(sum(h.mv_base_ccy)/100000000 as decimal(28,6)) as nav_per_unit
from {{ ref('int_holdings_enriched') }} h
group by h.fund_id, h.position_date
