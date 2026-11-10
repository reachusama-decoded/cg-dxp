-- Runs once, at the database's first start: the postgres image executes every .sql in /docker-entrypoint-initdb.d
-- when its data directory is empty. It creates the running example's price sheet (contract section 2, the
-- consumer-aligned table rpt_eod_prices_us) and loads it from the read-only /seed mount.
create table eod_prices (
    price_key        text primary key,    -- instrument_id || '|' || price_date, STTM rule 11
    instrument_id    text not null,       -- the ISIN, rule 1
    ticker           text,
    instrument_name  text,
    price_date       date not null,
    price_native     numeric(18, 6),
    native_ccy       char(3),
    fx_rate_to_usd   numeric(18, 8),
    price_usd        numeric(18, 6) not null,
    price_source     text,
    vendor_ts        timestamp
);

copy eod_prices from '/seed/rpt_eod_prices_us.csv' with (format csv, header true);
