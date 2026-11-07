{% test non_negative(model, column_name) %}
-- Generic test: fails when the column holds any negative value.
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
