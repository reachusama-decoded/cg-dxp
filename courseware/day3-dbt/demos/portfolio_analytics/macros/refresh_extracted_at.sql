{#- Seed post-hook: stamp the raw feed as extracted "now" so freshness checks pass.
    dbt compares loaded_at with the current time in UTC, so the stamp must be UTC too: on DuckDB the
    column has no time zone, and a local-time stamp would look hours old anywhere west of Greenwich. -#}
{% macro refresh_extracted_at(relation) -%}
  {%- if target.type == 'duckdb' -%}
  update {{ relation }} set _extracted_at = (now() at time zone 'UTC')
  {%- else -%}
  update {{ relation }} set _extracted_at = {{ dbt.current_timestamp() }}
  {%- endif -%}
{%- endmacro %}
