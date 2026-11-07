-- Direct mappings plus type and case normalisation. Nothing filtered here: the US and
-- active filters belong to the consumer-aligned mart, where the contract states them.
select
    upper(trim(isin))         as instrument_id,
    upper(trim(ticker))       as ticker,
    trim(instrument_name)     as instrument_name,
    upper(trim(market))       as market,
    upper(trim(trade_ccy))    as trade_ccy,
    is_active
from {{ source('refdata', 'instrument_master_raw') }}
