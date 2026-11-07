-- Consumer-aligned product (agg_): trading activity per instrument, one row per instrument.
-- Aggregates the canonical trade fact (joined to the canonical instrument) into quantity
-- traded, value traded, and trade count. Feeds the instrument dashboard and the trade-count
-- reconciliation test.
select
  t.instrument_id,
  i.ticker,
  i.asset_class,
  i.sector,
  sum(t.qty) as qty_traded,
  sum(t.gross_value) as value_traded,
  count(*) as trades
from {{ ref('dom_trading__trade') }} t
join {{ ref('dom_instrument__instrument') }} i using (instrument_id)
group by t.instrument_id, i.ticker, i.asset_class, i.sector
