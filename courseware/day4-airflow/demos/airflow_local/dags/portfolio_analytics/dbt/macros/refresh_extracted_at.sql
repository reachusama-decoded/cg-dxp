{#- Seed post-hook: stamp the raw feed as extracted "now" so freshness checks pass. -#}
{% macro refresh_extracted_at(relation) -%}
  update {{ relation }} set _extracted_at = {{ dbt.current_timestamp() }}
{%- endmacro %}
