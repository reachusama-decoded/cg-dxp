-- Consumer-aligned product (agg_): fund net asset value, one row per fund. Joins the
-- canonical fund holdings to the canonical latest price, weights by holding %, and sums to
-- a NAV per 100 units. Read by the fund-analytics dashboard.
select
  f.fund_id,
  f.name,
  f.style,
  count(*) as holdings,
  sum(h.weight_pct / 100.0 * lp.last_price) as nav_per_100_units
from {{ ref('dom_fund__fund') }} f
join {{ ref('dom_fund__holding') }} h using (fund_id)
join {{ ref('dom_trading__latest_price') }} lp using (instrument_id)
group by f.fund_id, f.name, f.style
