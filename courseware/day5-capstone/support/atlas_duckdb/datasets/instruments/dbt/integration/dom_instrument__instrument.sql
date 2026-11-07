-- Domain-aligned product · Instrument domain. The canonical security, one row per
-- instrument. Upper-cases ticker and ccy, trims the descriptive fields, and drops
-- non-positive ids. The conformed security master every valuation and activity mart joins to.
select
  instrument_id,
  upper(trim(ticker)) as ticker,
  trim(name) as name,
  trim(asset_class) as asset_class,
  trim(sector) as sector,
  upper(trim(ccy)) as ccy
from {{ ref('src_secmaster__instruments') }}
where instrument_id > 0
