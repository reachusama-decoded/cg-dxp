-- Domain-aligned product · Positions domain. The canonical position, one row per
-- portfolio/instrument. Nets signed_qty from the canonical trade fact, marks it at the
-- canonical latest price for market value, and sums bought/sold, fees, and trade count.
-- This is the shared position grain the consumer marts roll up -- the Atlas analogue of
-- the course-wide client_positions data product. Replaces the old generic curated_positions.
-- Materialised as a table since rpt_portfolio_summary and rpt_portfolio_performance reuse it.
{{ config(materialized='table') }}

select
  t.portfolio_id,
  t.instrument_id,
  i.ticker,
  i.asset_class,
  i.sector,
  sum(t.signed_qty) as net_qty,
  sum(t.signed_qty) * max(lp.last_price) as market_value,
  sum(case when t.direction = 1 then t.gross_value else 0 end) as total_bought,
  sum(case when t.direction = -1 then t.gross_value else 0 end) as total_sold,
  sum(t.fee) as fees,
  count(*) as trades
from {{ ref('dom_trading__trade') }} t
join {{ ref('dom_trading__latest_price') }} lp using (instrument_id)
join {{ ref('dom_instrument__instrument') }} i using (instrument_id)
group by
  t.portfolio_id,
  t.instrument_id,
  i.ticker,
  i.asset_class,
  i.sector
