# Price sheet: consumer guide

## What is this data product?

End-of-day prices for each instrument, in its own currency and in US dollars. Refreshed every weekday by
**07:30 UK**, from the vendor's close prices and the day's FX rates.

## Where do I find it?

| Table | Grain | Use it for |
|---|---|---|
| `fct_prices_usd` | one row per instrument per day | the price in its own currency, the FX rate used, and the price in US dollars |
| `agg_prices_by_ccy` | one row per day | how many prices arrived in each currency |

## Sample query

```sql
select instrument_id, price_date, native_ccy, price_native, fx_rate_to_usd, price_usd
from fct_prices_usd
where price_date = (select max(price_date) from fct_prices_usd)
order by instrument_id
```

## Known limitations

- Prices are end of day only; there are no intraday prices.
- A price with no FX rate for its day is not published: the `not_null` test on `price_usd` stops the run.

## Freshness and support

The feed must be less than 6 hours old when the run starts, or nothing is published and yesterday's price
sheet stands. Questions: the pricing data team's Teams channel.
