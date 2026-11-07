{#
  Compatibility macro. No-op for prototypes.
#}

{% macro cspn_commit_checkpoints() -%}
  {{ return('') }}
{%- endmacro %}
