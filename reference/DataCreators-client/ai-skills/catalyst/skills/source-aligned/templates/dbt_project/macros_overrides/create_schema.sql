{#
  Casper Source-Aligned no-op schema creation for environments without CREATE SCHEMA permission.
#}

{% macro create_schema(relation) -%}
  {{ return('') }}
{%- endmacro %}
