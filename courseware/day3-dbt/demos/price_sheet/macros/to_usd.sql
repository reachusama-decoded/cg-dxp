{# to_usd: the conversion rule, written once. A macro is a function that returns SQL text. #}
{% macro to_usd(amount, ccy, rate) %}
    cast({{ amount }} * case when {{ ccy }} = 'USD' then 1.0 else {{ rate }} end as decimal(18, 6))
{% endmacro %}
