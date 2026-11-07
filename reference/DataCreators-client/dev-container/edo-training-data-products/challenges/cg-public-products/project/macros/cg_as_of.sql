{# AUTHOR lane M: parameterized safe two-clock predicate, not a hard-coded fee conversion. #}
{% macro cg_as_of_predicate(history_alias, business_expr, knowledge_expr,
 business_from='business_valid_from', business_to='business_valid_to',
 system_from='system_valid_from', system_to='system_valid_to') %}
 {% if var('enable_phase_3', false) %}
  {{ exceptions.raise_compiler_error('Complete the temporal macro before enabling phase 3') }}
 {% else %}
  1=0 {# Disabled-node parser placeholder; never a completed as-of predicate. #}
 {% endif %}
{% endmacro %}
