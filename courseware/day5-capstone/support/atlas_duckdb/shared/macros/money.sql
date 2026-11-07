{# Reusable money macros: name the repeated cents/basis-point arithmetic once
   so every model uses the same, consistent expression instead of scattered
   magic numbers. Same {% macro %}/{% endmacro %} shape as epoch_date.sql. #}

{% macro cents_to_decimal(column_name) -%}
  {# integer cents -> decimal currency units #}
  {{ column_name }} / 100.0
{%- endmacro %}


{% macro basis_points(amount_column, bps_column) -%}
  {# apply a basis-point rate to an amount: one basis point is 1/10000, so the
     fee on an amount is amount * bps / 10000. #}
  {{ amount_column }} * {{ bps_column }} / 10000.0
{%- endmacro %}
