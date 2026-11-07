{#
  No-op override for add_default_metric (EMR-only macro from caspian-libs).
  Required so prepared model post_hooks compile without error in Databricks prototypes.
#}

{% macro add_default_metric(schema) -%}
  {{ return('') }}
{%- endmacro %}
