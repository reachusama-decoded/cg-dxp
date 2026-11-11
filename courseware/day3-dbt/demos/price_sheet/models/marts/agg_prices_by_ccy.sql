-- agg_prices_by_ccy: one column per currency, written by a loop instead of by hand
{% set currencies = ['USD', 'EUR', 'GBP', 'JPY'] %}

select
    price_date,
    {% for ccy in currencies %}
    count(case when native_ccy = '{{ ccy }}' then 1 end) as prices_in_{{ ccy | lower }}{% if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('fct_prices_usd') }}
group by price_date
order by price_date
