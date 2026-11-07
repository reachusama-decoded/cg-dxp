-- Consumer-aligned product (ts_): daily trading activity broken down by asset class
-- (Equity, Bond, ETF, Commodity), with a 7-day rolling traded-value column for
-- trend-spotting.
--
-- The per-day aggregate is built first in a CTE, then the window sum is layered over it so
-- the rolling frame sees one row per (asset_class, trade_date). Money is in native trade
-- currency and is NOT FX-converted -- a known simplification of this teaching dataset.
with daily as (
  select
    t.trade_date,
    i.asset_class,
    sum(t.gross_value) as traded_value,
    sum(t.fee)         as fees,
    count(*)           as trades
  from {{ ref('dom_trading__trade') }} t
  join {{ ref('dom_instrument__instrument') }} i using (instrument_id)
  group by t.trade_date, i.asset_class
)

select
  trade_date,
  asset_class,
  traded_value,
  fees,
  trades,
  sum(traded_value) over (
    partition by asset_class
    order by trade_date
    rows between 6 preceding and current row
  ) as rolling_7d_value
from daily
