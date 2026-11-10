# Sample data: the sources as landed, and the price sheet as published

Five CSV files, small enough to read, that make the schema question concrete. The contract's schema (section 2 of `03-data-contract.md`) describes the **target**, `rpt_eod_prices_us.csv`: the table consumers receive, and the only shape they may depend on. The **sources** keep their own shapes: the vendor's column names, the vendor's casing, the vendor's duplicates. The mapping in `04-sttm.md` is the route from the three source files to the target. The dbt project in `day2-platform/demos/contract-to-code/eod_prices/` runs that route; the intermediate and target files here were exported from its build (`dbt build`, 20 tests passing).

| File | Alignment | Columns | Rows | What it is |
|---|---|---|---|---|
| `vendor_prices_raw.csv` | Source-aligned, as landed | `isin, px_date, px_close, px_ccy, vendor_ts, _received_at` | 36 | The vendor's end-of-day feed for 3, 4 and 5 November 2026: twelve instruments, one re-delivery, a lower-case currency code, one missing row |
| `instrument_master_raw.csv` | Source-aligned, as landed | `isin, ticker, instrument_name, market, trade_ccy, is_active` | 12 | Reference data: nine US instruments (one inactive) and three listed in London, Frankfurt and Tokyo |
| `fx_rates_raw.csv` | Source-aligned, as landed | `from_ccy, to_ccy, rate_dt, rate, _received_at` | 9 | Same-day closes to USD for GBP, EUR and JPY |
| `int_prices_usd.csv` | Domain-aligned | the target's columns plus `market` and `is_active` | 35 | Every instrument, deduplicated, FX applied, the firm's rules once; the London team's sheet is a different filter on this table |
| `rpt_eod_prices_us.csv` | Consumer-aligned: the contract's schema | the eleven columns of contract section 2, in that order | 24 | Active US-listed instruments, one row per instrument per business date, prices in USD |

## Where each mapping rule shows in the data

| Rule in `04-sttm.md` | Look at |
|---|---|
| R1 dedup: the later `vendor_ts` wins | Apple on 4 November: two vendor rows (21:05 at 230.801, 22:40 at 231.151); the target carries 231.151 with `vendor_ts` 22:40 |
| R2 filter: `market = 'US'` and `is_active` | HSBC, SAP and Toyota are in the sources and in `int_prices_usd.csv`, not in the target; so is Johnson & Johnson, `is_active = false` |
| Rule 6: upper-case the currency | HSBC's `px_ccy` is `gbp` in the feed and `GBP` from staging onwards |
| Rule 7: same-day FX by currency and date | In `int_prices_usd.csv`, HSBC on 3 November: 6.9883 GBP × 1.267013 = 8.854267 USD; US rows carry the constant 1.0 |
| R4: a missing instrument is a missing row | SAP has no vendor row on 5 November: no row in any layer, not a null price |
| Rule 11: the key | `price_key` is `instrument_id`, a bar, `price_date`; unique across the 24 rows |

## Source schema or consumer schema?

The contract's schema is the consumer's. It is what the producer promises to deliver, so it is written in the consumer's terms (`price_usd`, `instrument_name`) rather than the vendor's (`px_close`, `isin`). The sources are named in the contract's identity section and described column by column only in the mapping (the `Source` column of `04-sttm.md`) and in dbt's `sources.yml`. A vendor renaming `px_close` is the producer's problem, absorbed in staging without telling anyone; a change to the eleven columns here is a contract change, under the versioning rules of section 6.
