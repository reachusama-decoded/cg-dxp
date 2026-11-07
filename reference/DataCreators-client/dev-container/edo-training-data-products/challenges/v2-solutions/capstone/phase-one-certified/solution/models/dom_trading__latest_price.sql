-- Domain-aligned product · Trading domain. The canonical current mark per instrument, one
-- row per instrument. Ranks the canonical trade fact by ts (tie-broken on trade_id) and
-- keeps the newest row. The shared "latest price" every valuation reads: the consumer
-- api_latest_price lookup and dom_positions__position both build on it, so the mark is
-- defined once. Materialised as a table since several models reuse it.
{{ config(materialized='table') }}

with ranked as (
  select
    instrument_id,
    price as last_price,
    ts as last_ts,
    row_number() over (
      partition by instrument_id
      order by ts desc, trade_id desc
    ) as rn
  from {{ ref('dom_trading__trade') }}
)

select
  instrument_id,
  last_price,
  last_ts
from ranked
where rn = 1
