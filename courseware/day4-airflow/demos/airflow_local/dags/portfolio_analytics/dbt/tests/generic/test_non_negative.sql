{#- Custom generic test: fails on any row where the column is negative.
    Usage in YAML:  tests: [non_negative]  -#}
{% test non_negative(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
