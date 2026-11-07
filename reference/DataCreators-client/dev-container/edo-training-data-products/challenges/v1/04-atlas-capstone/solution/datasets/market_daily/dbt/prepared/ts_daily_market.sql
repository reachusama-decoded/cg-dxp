-- Consumer-aligned product (ts_): daily market activity, one row per trade_date. Aggregates
-- the canonical trade fact into traded value, fees, and trade count per day. Read by the
-- market dashboard and the trade-count reconciliation test; ts_daily_market_incremental is
-- its twin.
select
  trade_date,
  sum(gross_value) as traded_value,
  sum(fee) as fees,
  count(*) as trades
from {{ ref('dom_trading__trade') }}
group by trade_date
