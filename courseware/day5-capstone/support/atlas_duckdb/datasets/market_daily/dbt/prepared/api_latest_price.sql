-- Consumer-aligned product (api_): the published latest-price lookup, one row per
-- instrument. A thin single-row-lookup view over the canonical dom_trading__latest_price,
-- so apps and marts read a stable, purpose-named surface without knowing how the mark is
-- derived.
select
  instrument_id,
  last_price,
  last_ts
from {{ ref('dom_trading__latest_price') }}
