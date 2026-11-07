{#
  Casper Source-Aligned utility macros.
#}

{% macro cspn_source(source_schema, table_name) -%}
  {%- set catalog = (target.catalog if target.catalog is defined and target.catalog else target.database) -%}
  {{ catalog }}.{{ source_schema }}.{{ table_name }}
{%- endmacro %}
