{#
  Casper Domain-Aligned surrogate key helper.

  Generates dl_row_uid from a list of natural key columns using SHA-256.
  Compatible with the source-aligned version but simplified for domain models.
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
    {{ exceptions.raise_compiler_error('Missing surrogate key columns; expected `meta.surrogate_key_cols`') }}
  {% endif %}

  {{ generated__surrogate_key_expr(cols) }} as dl_row_uid
{%- endmacro %}
