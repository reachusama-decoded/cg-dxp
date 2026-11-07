{% macro generate_schema_name(custom_schema_name, node) -%}
  {% if custom_schema_name is not none and custom_schema_name != target.schema and node.resource_type != 'test' %}
    {{ exceptions.raise_compiler_error('Extra schemas are outside the assigned route') }}
  {% endif %}
  {{ target.schema }}
{%- endmacro %}
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
  {{ env_var('DC_RELATION_PREFIX') }}_{{ custom_alias_name if custom_alias_name else node.name }}
{%- endmacro %}
