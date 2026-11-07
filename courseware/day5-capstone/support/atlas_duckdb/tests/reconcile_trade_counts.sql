-- Reconciliation: the three marts that count trades must agree.
-- Every valid trade is counted once in dom_positions__position, ts_daily_market and
-- agg_instrument_activity, so sum(trades) must match across all three.
-- Returns a row (test FAILS) only when the totals diverge.
select
  (select sum(trades) from {{ ref('dom_positions__position') }}) as position_trades,
  (select sum(trades) from {{ ref('ts_daily_market') }}) as daily_trades,
  (select sum(trades) from {{ ref('agg_instrument_activity') }}) as instrument_trades
where (select sum(trades) from {{ ref('dom_positions__position') }})
   != (select sum(trades) from {{ ref('ts_daily_market') }})
   or (select sum(trades) from {{ ref('dom_positions__position') }})
   != (select sum(trades) from {{ ref('agg_instrument_activity') }})
