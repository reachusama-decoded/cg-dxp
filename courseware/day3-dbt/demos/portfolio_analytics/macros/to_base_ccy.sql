{#- A small reusable macro: convert a local-currency amount with an optional FX rate.
    Used by the stretch model so learners see where a macro earns its place. -#}
{% macro to_base_ccy(amount_col, rate_col) -%}
  cast(cast({{ amount_col }} as decimal(19, 2)) * coalesce({{ rate_col }}, 1.0) as decimal(18, 2))
{%- endmacro %}
