{% macro native_value(value, rate) %}cast(cast({{ value }} as decimal(28,2)) * {{ rate }} as decimal(28,2)){% endmacro %}
