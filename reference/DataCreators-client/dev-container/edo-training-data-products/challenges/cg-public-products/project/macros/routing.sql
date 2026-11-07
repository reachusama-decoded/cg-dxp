{# Supplied routing plumbing. Keep writes inside the assigned catalog/schema. #}
{# dbt gives every data test the custom schema dbt_test__audit; route it to the assigned schema. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
  {% if custom_schema_name is not none and custom_schema_name != target.schema and node.resource_type != 'test' %}
    {{ exceptions.raise_compiler_error('Extra schemas are outside the assigned classroom route') }}
  {% endif %}
  {{ target.schema }}
{%- endmacro %}
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
  {% set prefix = env_var('DC_RELATION_PREFIX') %}
  {% if not modules.re.fullmatch('[a-z][a-z0-9_]{2,55}', prefix) %}
    {{ exceptions.raise_compiler_error('Use a valid unique owned DC_RELATION_PREFIX') }}
  {% endif %}
  {{ prefix }}_{{ custom_alias_name if custom_alias_name else node.name }}
{%- endmacro %}
