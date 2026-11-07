{% macro epoch_date(column_name) -%}
  {%- if target.type == 'databricks' -%}
    {# epoch SECONDS -> UTC calendar date, timezone-independent (avoids session-tz day shifts) #}
    date_from_unix_date(cast({{ column_name }} / 86400 as int))
  {%- else -%}
    {# non-Databricks fallback for the designer's local structural compile; the shipped target is always Databricks #}
    cast(to_timestamp({{ column_name }}) as date)
  {%- endif -%}
{%- endmacro %}
