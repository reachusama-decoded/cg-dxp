# Source-to-target mapping: `rpt_eod_prices_us`

Target grain: one row per active, US-listed instrument per business date. Sources: `vendor_feed.vendor_prices_raw` (V), `refdata.instrument_master_raw` (I), `fx_feed.fx_rates_raw` (F). Rule types are the textbook five the room elicits on Day 2 (direct, constant, lookup, aggregate, derive) plus the row-level rules (filter, dedup) that any mapping needs. Catalyst's taxonomy splits derive further; the mapping is the same.

## Column rules

| # | Target column | Type | Rule type | Source | Rule, in English precise enough to implement |
|---|---|---|---|---|---|
| 1 | `instrument_id` | STRING | Direct | V.isin | Trim, upper-case. Null ISIN: row rejected (see row rules). |
| 2 | `ticker` | STRING | Lookup | I.ticker by ISIN | Join I on `upper(trim(isin))`. Exactly one master row per ISIN; a missing master row leaves ticker null and fails the relationship test. |
| 3 | `instrument_name` | STRING | Lookup | I.instrument_name by ISIN | As above. Trimmed. |
| 4 | `price_date` | DATE | Direct | V.px_date | Cast to date. The business date of the close, not the delivery timestamp. |
| 5 | `price_native` | DECIMAL(18,6) | Direct | V.px_close | Cast. Zero or negative is a data quality failure, not a filter. |
| 6 | `native_ccy` | STRING | Direct | V.px_ccy | Upper-case. ISO 4217. |
| 7 | `fx_rate_to_usd` | DECIMAL(18,8) | Lookup / Constant | F.rate by (from_ccy = native_ccy, to_ccy = 'USD', rate_dt = price_date) | Constant `1.0` when `native_ccy = 'USD'`. No match for a non-USD currency: leave null (never default to 1.0). |
| 8 | `price_usd` | DECIMAL(18,6) | Derive | 5 × 7 | `price_native * fx_rate_to_usd`; null when the rate is null, so the `not_null` test fails the build. |
| 9 | `price_source` | STRING | Constant | — | `'VENDOR'`. `'MANUAL'` is reserved for an override process that does not exist yet. |
| 10 | `vendor_ts` | TIMESTAMP | Direct | V.vendor_ts | The vendor's own timestamp of the delivery that supplied the price (after dedup). |
| 11 | `price_key` | STRING | Derive | 1, 4 | `instrument_id || '|' || price_date`; unique. |

## Row rules

| # | Rule type | Rule |
|---|---|---|
| R1 | Dedup | Several vendor rows for the same (ISIN, date) are deliveries of the same price; keep the row with the latest `vendor_ts`. |
| R2 | Filter | Keep instruments where `I.market = 'US'` and `I.is_active`. Inactive and non-US instruments are excluded from the sheet, not from the intermediate layer, so the London team's version is a filter change. |
| R3 | Reject | A vendor row with a null ISIN or null date cannot be placed and is dropped in staging; the count of dropped rows is logged. |
| R4 | Null meaning | `fx_rate_to_usd` null means "no same-day rate received"; `price_usd` is then null and the build fails. A missing instrument on a date is a missing row, not a null price. |

## Edge cases agreed in the interview

- Re-delivered vendor files: later `vendor_ts` wins (R1); both deliveries stay in the landed table so the history is answerable.
- Same-day FX only (rule 7). Yesterday's rate is wrong, not a fallback.
- A price that moves more than 5% day on day is published and flagged for the duty-to-explain (see `service-levels.md`); it is not suppressed.
- Dual listings: the master carries one primary ISIN per instrument; the vendor's secondary-listing rows do not match `market = 'US'` and drop out at R2.
- Weekends and US market holidays: no rows expected; the schedule skips them.
