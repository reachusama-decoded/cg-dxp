{#
  Naming override for Databricks (Unity Catalog).
  Treats custom_schema_name as the full schema name (no suffix concatenation).
#}

{% macro databricks__generate_schema_name(custom_schema_name, node) -%}
  {%- if custom_schema_name is none -%}
    {{ target.schema | trim }}
  {%- else -%}
    {{ custom_schema_name | trim }}
  {%- endif -%}
{%- endmacro %}
