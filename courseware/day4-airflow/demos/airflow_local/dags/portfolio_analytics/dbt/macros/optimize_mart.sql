{#- Post-hook for mart tables. Databricks: Delta OPTIMIZE + ZORDER, as in the learners'
    project. Anything else: a no-op statement, so the same project runs on DuckDB. -#}
{% macro optimize_mart(relation) -%}
  {%- if target.type == 'databricks' -%}
    optimize {{ relation }} zorder by (fund_id, position_date)
  {%- else -%}
    select 1 as optimize_mart_noop_on_{{ target.type }}
  {%- endif -%}
{%- endmacro %}
