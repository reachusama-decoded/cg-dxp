{# AUTHOR lane M: invalid ranges and simultaneous business/system overlap. #}
{% test cg_temporal_integrity(model) %}
 {% if var('enable_phase_3', false) %}
  {{ exceptions.raise_compiler_error('Complete the generic temporal-integrity test') }}
 {% else %}
  select cast(null as string) as row_uid where 1=0
 {% endif %}
{% endtest %}
