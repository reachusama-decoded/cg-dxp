-- A singular test: a query that returns the rows that break the rule. No rows, the test passes.
-- Rule: one price per instrument per day.
select instrument_id, price_date, count(*) as prices
from {{ ref('prices_usd') }}
group by instrument_id, price_date
having count(*) > 1
