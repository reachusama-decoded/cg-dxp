select fund_id, instrument_id, cast(market_value as decimal(18,2)) as market_value
from {{ source('training', 'holdings') }}
