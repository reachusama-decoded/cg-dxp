#!/usr/bin/env python3
"""Generate the Day 2 contract-to-code example: the 'US end-of-day instrument prices' data
product as a dbt-duckdb project with synthetic seeds. This is the reference for what a
Catalyst/Copilot generation from the running-example contract should look like.
Writes courseware/day2-platform/demos/contract-to-code/eod_prices/."""
import csv, pathlib, random, shutil, textwrap, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parents[2]
DST = ROOT / "courseware/day2-platform/demos/contract-to-code/eod_prices"
if DST.exists():
    shutil.rmtree(DST)
for d in ["seeds", "models/staging", "models/intermediate", "models/marts", "tests", "macros"]:
    (DST / d).mkdir(parents=True)

def w(rel, text):
    (DST / rel).write_text(textwrap.dedent(text).lstrip("\n"))

# ---------- synthetic seeds (deterministic) ----------
rnd = random.Random(7)
instruments = [
    ("US0378331005", "AAPL", "Apple Inc", "US", "USD", True),
    ("US5949181045", "MSFT", "Microsoft Corp", "US", "USD", True),
    ("US0231351067", "AMZN", "Amazon.com Inc", "US", "USD", True),
    ("US30303M1027", "META", "Meta Platforms", "US", "USD", True),
    ("US67066G1040", "NVDA", "NVIDIA Corp", "US", "USD", True),
    ("US88160R1014", "TSLA", "Tesla Inc", "US", "USD", True),
    ("US46625H1005", "JPM", "JPMorgan Chase", "US", "USD", True),
    ("US4781601046", "JNJ", "Johnson & Johnson", "US", "USD", False),   # inactive: excluded by rule
    ("GB0005405286", "HSBA", "HSBC Holdings", "GB", "GBP", True),
    ("DE0007164600", "SAP", "SAP SE", "DE", "EUR", True),
    ("JP3633400001", "7203", "Toyota Motor", "JP", "JPY", True),
    ("US9311421039", "WMT", "Walmart Inc", "US", "USD", True),
]
dates = [dt.date(2026, 11, 3), dt.date(2026, 11, 4), dt.date(2026, 11, 5)]
base = {"AAPL": 231.5, "MSFT": 428.1, "AMZN": 201.2, "META": 590.4, "NVDA": 139.8, "TSLA": 258.6,
        "JPM": 224.9, "JNJ": 160.3, "HSBA": 7.12, "SAP": 214.7, "7203": 2745.0, "WMT": 85.4}
with open(DST / "seeds/vendor_prices_raw.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["isin", "px_date", "px_close", "px_ccy", "vendor_ts", "_received_at"])
    for d in dates:
        for isin, tkr, _, mkt, ccy, _ in instruments:
            if tkr == "SAP" and d == dates[-1]:
                continue  # vendor missed one non-US price on the last day
            px = round(base[tkr] * (1 + rnd.uniform(-0.02, 0.02)), 4 if ccy != "JPY" else 1)
            ts = f"{d} 21:05:00"
            wr.writerow([isin, d, px, ccy.lower() if tkr == "HSBA" else ccy, ts, f"{d} 21:10:00"])
            if tkr == "AAPL" and d == dates[1]:   # a corrected re-delivery: later vendor_ts wins
                wr.writerow([isin, d, round(px + 0.35, 4), ccy, f"{d} 22:40:00", f"{d} 22:45:00"])
with open(DST / "seeds/instrument_master_raw.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["isin", "ticker", "instrument_name", "market", "trade_ccy", "is_active"])
    for isin, tkr, name, mkt, ccy, act in instruments:
        wr.writerow([isin, tkr, name, mkt, ccy, str(act).lower()])
with open(DST / "seeds/fx_rates_raw.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["from_ccy", "to_ccy", "rate_dt", "rate", "_received_at"])
    fx = {"GBP": 1.27, "EUR": 1.08, "JPY": 0.0066}
    for d in dates:
        for c, r in fx.items():
            wr.writerow([c, "USD", d, round(r * (1 + rnd.uniform(-0.004, 0.004)), 6), f"{d} 17:00:00"])

# ---------- project ----------
w("dbt_project.yml", """
    # US end-of-day instrument prices — the Day 2 contract-to-code example.
    # Generated from the running-example data contract (courseware/common/running-example/).
    name: 'eod_prices'
    version: '1.0'
    profile: 'eod_prices'
    config-version: 2
    model-paths: ["models"]
    seed-paths: ["seeds"]
    test-paths: ["tests"]
    macro-paths: ["macros"]
    target-path: "target"
    clean-targets: ["target", "dbt_packages"]

    models:
      eod_prices:
        staging:
          +materialized: view
          +tags: ["staging"]
        intermediate:
          +materialized: view
          +tags: ["intermediate"]
        marts:
          +materialized: table
          +tags: ["marts"]

    seeds:
      eod_prices:
        vendor_prices_raw:
          +post-hook: "update {{ this }} set _received_at = {{ dbt.current_timestamp() }}"
        fx_rates_raw:
          +post-hook: "update {{ this }} set _received_at = {{ dbt.current_timestamp() }}"
    """)
w("profiles.yml", """
    eod_prices:
      target: local
      outputs:
        local:
          type: duckdb
          path: "{{ env_var('EOD_DUCKDB_PATH', 'warehouse/eod_prices.duckdb') }}"
          schema: "{{ env_var('EOD_SCHEMA', 'training_demo') }}"
          threads: 4
    """)
w("models/sources.yml", """
    version: 2

    sources:
      - name: vendor_feed
        description: "Global end-of-day close prices from the pricing vendor (SFTP drop, native currency)."
        database: "{{ target.database }}"
        schema: "{{ target.schema }}"
        config:
          loaded_at_field: _received_at
          freshness:
            warn_after:  {count: 12, period: hour}
            error_after: {count: 24, period: hour}
        tables:
          - name: vendor_prices_raw
            description: "One row per instrument per day per delivery; a re-delivery has a later vendor_ts."
            columns:
              - name: isin
              - name: px_date
              - name: px_close
              - name: px_ccy
              - name: vendor_ts
      - name: refdata
        description: "Internal instrument master."
        database: "{{ target.database }}"
        schema: "{{ target.schema }}"
        tables:
          - name: instrument_master_raw
      - name: fx_feed
        description: "Daily FX closes to a USD base."
        database: "{{ target.database }}"
        schema: "{{ target.schema }}"
        config:
          loaded_at_field: _received_at
          freshness:
            warn_after:  {count: 12, period: hour}
            error_after: {count: 24, period: hour}
        tables:
          - name: fx_rates_raw
    """)
w("models/staging/stg_vendor_prices.sql", """
    -- STTM rule: one price per instrument per date; when the vendor re-delivers, the latest
    -- vendor_ts wins (lookup-free dedup). Currency codes are normalised to upper case.
    with src as (
        select * from {{ source('vendor_feed', 'vendor_prices_raw') }}
    ),

    deduped as (
        select
            upper(trim(isin))                         as instrument_id,
            cast(px_date as date)                     as price_date,
            cast(px_close as decimal(18, 6))          as price_native,
            upper(trim(px_ccy))                       as native_ccy,
            cast(vendor_ts as timestamp)              as vendor_ts,
            _received_at,
            row_number() over (
                partition by upper(trim(isin)), cast(px_date as date)
                order by cast(vendor_ts as timestamp) desc
            )                                         as rn
        from src
        where isin is not null and px_date is not null
    )

    select instrument_id, price_date, price_native, native_ccy, vendor_ts, _received_at
    from deduped
    where rn = 1
    """)
w("models/staging/stg_instruments.sql", """
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
    """)
w("models/staging/stg_fx_rates.sql", """
    -- Only USD-base rates are relevant to this product (contract: prices reported in USD).
    select
        upper(from_ccy)                as from_ccy,
        upper(to_ccy)                  as to_ccy,
        cast(rate_dt as date)          as rate_date,
        cast(rate as decimal(18, 8))   as fx_rate
    from {{ source('fx_feed', 'fx_rates_raw') }}
    where upper(to_ccy) = 'USD'
    """)
w("models/intermediate/int_prices_usd.sql", """
    -- Lookup + derive: instrument attributes by instrument_id, FX by (currency, date);
    -- price_usd = price_native x rate, with USD a constant rate of 1. A non-USD price with no
    -- rate for that date stays NULL so the mart's not_null test catches it (no silent 1.0).
    with prices as (
        select * from {{ ref('stg_vendor_prices') }}
    ),

    instruments as (
        select * from {{ ref('stg_instruments') }}
    ),

    fx as (
        select * from {{ ref('stg_fx_rates') }}
    )

    select
        p.instrument_id,
        i.ticker,
        i.instrument_name,
        i.market,
        i.is_active,
        p.price_date,
        p.price_native,
        p.native_ccy,
        case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end     as fx_rate_to_usd,
        cast(cast(p.price_native as decimal(19, 6))
             * case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end
             as decimal(18, 6))                                        as price_usd,
        p.vendor_ts,
        'VENDOR'                                                        as price_source
    from prices p
    left join instruments i
        on i.instrument_id = p.instrument_id
    left join fx f
        on f.from_ccy = p.native_ccy
        and f.rate_date = p.price_date
    """)
w("models/marts/rpt_eod_prices_us.sql", """
    -- Consumer-aligned: the US price sheet. Contract scope: active, US-listed instruments,
    -- one row per instrument per business date, prices in USD, delivered by 07:30 ET.
    select
        instrument_id || '|' || cast(price_date as varchar)  as price_key,
        instrument_id,
        ticker,
        instrument_name,
        price_date,
        price_native,
        native_ccy,
        fx_rate_to_usd,
        price_usd,
        price_source,
        vendor_ts
    from {{ ref('int_prices_usd') }}
    where market = 'US'
      and is_active
    """)
w("models/schema.yml", """
    version: 2

    models:
      - name: stg_vendor_prices
        description: "Deduplicated vendor prices, one row per instrument per date."
        columns:
          - name: instrument_id
            tests: [not_null]
          - name: price_date
            tests: [not_null]
      - name: stg_instruments
        columns:
          - name: instrument_id
            tests: [not_null, unique]
      - name: rpt_eod_prices_us
        description: "US end-of-day price sheet in USD (see the data contract)."
        columns:
          - name: price_key
            description: "instrument_id|price_date — the contract's grain."
            tests: [not_null, unique]
          - name: instrument_id
            tests:
              - not_null
              - relationships:
                  arguments:
                    to: ref('stg_instruments')
                    field: instrument_id
          - name: price_usd
            tests: [not_null]
          - name: price_source
            tests:
              - accepted_values:
                  arguments:
                    values: ['VENDOR', 'MANUAL']
    """)
w("tests/assert_us_completeness.sql", """
    -- Contract SLA: on the latest priced date, at least 99.5% of active US instruments must
    -- have a price. Returns a row (FAIL) when coverage is below that.
    with active_us as (
        select count(*) as expected from {{ ref('stg_instruments') }} where market = 'US' and is_active
    ),
    latest as (
        select max(price_date) as price_date from {{ ref('rpt_eod_prices_us') }}
    ),
    priced as (
        select count(*) as actual from {{ ref('rpt_eod_prices_us') }} where price_date = (select price_date from latest)
    )
    select actual, expected, actual * 1.0 / expected as coverage
    from priced, active_us
    where actual * 1.0 / expected < 0.995
    """)
w("tests/assert_no_future_prices.sql", """
    -- A price dated after the vendor timestamp cannot be right.
    select * from {{ ref('rpt_eod_prices_us') }}
    where price_date > cast(vendor_ts as date)
    """)
w(".gitignore", "target/\ndbt_packages/\nlogs/\nwarehouse/\n")
w("run.sh", """
    #!/usr/bin/env bash
    # Build the contract-to-code example on DuckDB and show the price sheet.
    set -euo pipefail
    cd "$(dirname "$0")"
    export EOD_DUCKDB_PATH="${EOD_DUCKDB_PATH:-$PWD/warehouse/eod_prices.duckdb}"
    mkdir -p warehouse
    dbt seed --full-refresh
    dbt source freshness
    dbt build
    dbt show --select rpt_eod_prices_us --limit 12
    """)
print("written", DST)
