{#
    Renders a schema name given a custom schema name. If the custom
    schema name is none, then the resulting schema is just the "schema"
    value in the specified target. Otherwise custom schema is used as it is.
    For the "local" target, always use default_schema so all models
    land in the user's personal schema.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if target.name == 'local' or custom_schema_name is none -%}
       {{ default_schema | trim}}
    {%- else -%}
       {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}

{#
Caspian Curation Libraries prohibits the automatic creation of schema objects. Schema objects
are considered as administrative objects and must be created externally.
As a practice, each schema should have its storage location. E.g.
    CREATE SCHEMA IF NOT EXISTS im_m_rdm LOCATION 's3a://datalake-prepared-dev1-us-west-2/im_m_rdm/'
#}
{% macro create_schema(relation) -%}
  {%- call statement('create_schema') -%}
    {% do exceptions.raise_database_error("Automatic schema creation is prohibited. Check your schema name '"
                                           ~ relation ~ "' or create it externally") %}
  {% endcall %}
{% endmacro %}
