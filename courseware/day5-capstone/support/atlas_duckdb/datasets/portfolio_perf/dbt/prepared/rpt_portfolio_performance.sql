-- Consumer-aligned product (rpt_): the richer executive mart, one row per portfolio with
-- AUM, fees, trading volume, net flow, and the blended realised fee rate. Builds on
-- rpt_portfolio_summary and folds in the buy/sell totals the canonical position already
-- sums per portfolio/instrument.
--
-- fee_bps_realized is the blended fee rate the client effectively paid in basis points:
-- total fees / total traded value * 10000, zero-guarded with nullif so a zero traded value
-- yields NULL rather than a divide-by-zero. Money is in native trade currency and is NOT
-- FX-converted -- a known simplification of this teaching dataset.
with positions as (
  select
    portfolio_id,
    sum(total_bought) as buy_value,
    sum(total_sold)   as sell_value
  from {{ ref('dom_positions__position') }}
  group by portfolio_id
)

select
  s.portfolio_id,
  s.aum,
  s.fees_paid,
  s.trades,
  s.positions,
  p.buy_value,
  p.sell_value,
  p.buy_value - p.sell_value as net_flow,
  -- traded_value is buys + sells; the realised rate is fees / traded_value * 10000,
  -- zero-guarded with nullif so a zero traded value yields NULL not a div-by-zero
  s.fees_paid / nullif(p.buy_value + p.sell_value, 0) * 10000 as fee_bps_realized
from {{ ref('rpt_portfolio_summary') }} s
join positions p using (portfolio_id)
