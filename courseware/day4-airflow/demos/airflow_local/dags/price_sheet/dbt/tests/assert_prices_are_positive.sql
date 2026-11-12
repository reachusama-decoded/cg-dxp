-- A test of your own: a query that returns the rows that break the rule. No rows, the test passes.
-- Rule: a price is never zero or negative.
select instrument_id, price_date, price_usd
from {{ ref('fct_prices_usd') }}
where price_usd <= 0
