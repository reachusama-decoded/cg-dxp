-- Domain-aligned product · Trading domain. The canonical trade fact, one row per valid
-- trade. Derives trade_date from the epoch ts, decodes side into direction/signed_qty,
-- converts price_cents -> price, computes gross_value and fee, and filters out non-positive
-- qty/price and bad sides. The conformed grain every consumer activity/position mart
-- aggregates from.
select
  trade_id,
  {{ epoch_date('ts') }} as trade_date,
  ts,
  portfolio_id,
  instrument_id,
  case side when 'B' then 1 else -1 end as direction,
  qty,
  {{ cents_to_decimal('price_cents') }} as price,
  qty * (price_cents / 100.0) as gross_value,
  qty * (price_cents / 100.0) * fee_bps / 10000.0 as fee,
  case side when 'B' then qty else -qty end as signed_qty,
  venue,
  upper(trim(ccy)) as ccy
from {{ ref('src_trading__trades') }}
where qty > 0
  and price_cents > 0
  and side in ('B', 'S')
