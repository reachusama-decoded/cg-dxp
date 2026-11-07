-- Consumer-aligned product (ts_): incremental twin of ts_daily_market. Same daily grain and
-- columns, but materialised incrementally so later runs only process trade dates newer than
-- what is already in the table. The first run builds all history; afterwards the
-- is_incremental() filter restricts to rows past the current max(trade_date), and
-- unique_key='trade_date' lets dbt replace (not duplicate) a re-run day. Money is in native
-- trade currency and is NOT FX-converted -- a known simplification of this teaching dataset.
{{ config(materialized='incremental', unique_key='trade_date') }}

select
  trade_date,
  sum(gross_value) as traded_value,
  sum(fee)         as fees,
  count(*)         as trades
from {{ ref('dom_trading__trade') }}
{% if is_incremental() %}
where trade_date > (select max(trade_date) from {{ this }})
{% endif %}
group by trade_date
