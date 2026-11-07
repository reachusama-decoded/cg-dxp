{#
  Casper Source-Aligned local v4 helpers.

  Goal: make the generated project runnable without depending on:
  - casper python context injection (modules.casper.* )
  - dbt_utils surrogate key macros

  These macros provide the columns expected by the v4 models:
  - generate_surrogate_key_v3() -> dl_row_uid
  - get_audit_cols()            -> audit + bitemporal columns
#}

{% macro generated__surrogate_key_expr(cols) -%}
  sha2(
    concat_ws(
      '|'
      {%- for c in cols %}
      , coalesce(cast({{ c }} as string), '')
      {%- endfor %}
    ),
    256
  )
{%- endmacro %}

{% macro generate_surrogate_key_v3(cols=None) -%}
  {% if cols is none %}
    {% set meta = (model.config.meta if model is defined and model.config is defined and model.config.meta is defined else None) %}
    {% if not meta %}
      {% set meta = (model.meta if model is defined and model.meta is defined else {}) %}
    {% endif %}
    {% set cols = meta.get('surrogate_key_cols', []) %}
  {% endif %}

  {% if cols is string %}
    {% set cols = [cols] %}
  {% endif %}

  {% if cols is none or (cols | length) == 0 %}
    {% set model_name = (model.name if model is defined and model.name is defined else this.identifier) %}
    {% if model_name in ['equity_namr_v4','equity_namr_cins_v4'] %}
      {% set cols = ['id_bb_unique'] %}
    {% else %}
      {{ exceptions.raise_compiler_error('Missing surrogate key columns; expected `meta.surrogate_key_cols`') }}
    {% endif %}
  {% endif %}

  {{ generated__surrogate_key_expr(cols) }} as dl_row_uid
{%- endmacro %}

{% macro get_audit_cols() -%}
  cast('{{ var('run_id', invocation_id) }}' as string) as dl_last_update_process_id,
  'Y' as dl_current_indicator,
  to_date('1900-01-01') as dl_business_start_date,
  to_date('9999-12-31') as dl_business_end_date,
  cast(current_timestamp() as timestamp) as dl_system_start_timestamp,
  cast('9999-12-31 23:59:59' as timestamp) as dl_system_end_timestamp
{%- endmacro %}
