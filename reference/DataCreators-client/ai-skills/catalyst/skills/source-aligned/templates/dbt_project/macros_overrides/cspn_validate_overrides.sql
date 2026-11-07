{#
adding support for upsert & upsert-scd2 strategy
#}
{% macro dbt_spark_validate_get_incremental_strategy(raw_strategy, file_format) %}

  {% set invalid_strategy_msg -%}
    Invalid incremental strategy provided: {{ raw_strategy }}
    Expected one of: 'append','merge', 'insert_overwrite', 'upsert', 'scd2', 'bitemporal_load', 'bitemporal_load_v2', 'match_merge', 'match_merge_alt_v2', 'match_merge_reference', 'match_merge_v2', 'delete_merge'
  {%- endset %}

  {% set invalid_merge_msg -%}
    Invalid incremental strategy provided: {{ raw_strategy }}
    You can only choose this strategy when file_format is set to 'delta'
  {%- endset %}

 {% set invalid_insert_overwrite_delta_msg -%}
    Invalid incremental strategy provided: {{ raw_strategy }}
    You cannot use this strategy when file_format is set to 'delta'
    Use the 'append' or 'merge' strategy instead
  {%- endset %}

  {% set invalid_insert_overwrite_endpoint_msg -%}
    Invalid incremental strategy provided: {{ raw_strategy }}
    You cannot use this strategy when connecting via endpoint
    Use the 'append' or 'merge' strategy instead
  {%- endset %}

  {% if raw_strategy not in ['append','merge', 'insert_overwrite','upsert', 'scd2', 'bitemporal_load', 'bitemporal_load_v2', 'match_merge', 'match_merge_alt_v2', 'match_merge_reference', 'match_merge_v2', 'delete_merge'] %}
    {% do exceptions.raise_compiler_error(invalid_strategy_msg) %}
  {%-else %}
    {% if raw_strategy == 'upsert' %}
      {% do dbt_spark_validate_upsert(file_format) %}
    {% endif %}
    {% if raw_strategy == 'scd2'  %}
      {% do dbt_spark_validate_scd2(file_format) %}
    {% endif %}
    {% if raw_strategy == 'bitemporal_load'  %}
      {% do dbt_spark_validate_bitemporal_load(file_format) %}
    {% endif %}
    {% if raw_strategy == 'bitemporal_load_v2'  %}
      {% do dbt_spark_validate_bitemporal_load(file_format) %}
    {% endif %}
    {% if raw_strategy in ['match_merge','match_merge_reference','match_merge_alt_v2']  %}
      {% do dbt_spark_validate_match_merge(file_format) %}
    {% endif %}
    {% if raw_strategy == 'match_merge_v2'  %}
      {% do dbt_spark_validate_match_merge(file_format) %}
    {% endif %}
    {% if raw_strategy == 'merge' and file_format != 'delta' %}
      {% do exceptions.raise_compiler_error(invalid_merge_msg) %}
    {% endif %}
    {% if raw_strategy == 'delete_merge' and file_format != 'delta' %}
      {% do exceptions.raise_compiler_error(invalid_merge_msg) %}
    {% endif %}
    {% if raw_strategy == 'insert_overwrite' and file_format == 'delta' %}
      {% do exceptions.raise_compiler_error(invalid_insert_overwrite_delta_msg) %}
    {% endif %}
    {% if raw_strategy == 'insert_overwrite' and target.endpoint %}
      {% do exceptions.raise_compiler_error(invalid_insert_overwrite_endpoint_msg) %}
    {% endif %}
  {% endif %}

  {% do return(raw_strategy) %}
{% endmacro %}

{#
macro for validating file_format in case of upsert
#}
{% macro dbt_spark_validate_upsert(file_format) %}
  {% set invalid_file_format_msg -%}
    You can only choose the 'upsert' incremental_strategy when file_format is set to 'parquet'
  {%- endset %}

  {% if file_format!='parquet' %}
    {% do exceptions.raise_compiler_error(invalid_file_format_msg) %}
  {% endif %}

{% endmacro %}

{#
macro for validating file_format in case of scd2
#}
{% macro dbt_spark_validate_scd2(file_format) %}
  {% set invalid_file_format_msg -%}
    You can only choose the 'scd2' incremental_strategy when file_format is set to 'parquet' or 'delta'
  {%- endset %}

  {% if file_format not in ['parquet','delta'] %}
    {% do exceptions.raise_compiler_error(invalid_file_format_msg) %}
  {% endif %}

{% endmacro %}

{#
macro for validating file_format in case of bitemporal_load and 'bitemporal_load_v2'
#}
{% macro dbt_spark_validate_bitemporal_load(file_format) %}
  {% set invalid_file_format_msg -%}
    You can only choose the 'bitemporal_load' and 'bitemporal_load_v2' strategy & load_type as ['incremental', 'full', 'balance', 'expire_merge_master', 'balance_full'] when file_format is set to 'delta'
  {%- endset %}

  {% if file_format not in ['delta'] %}
    {% do exceptions.raise_compiler_error(invalid_file_format_msg) %}
  {% endif %}

{% endmacro %}


{#
macro for validating file_format in case of match_merge
#}
{% macro dbt_spark_validate_match_merge(file_format) %}
  {% set invalid_file_format_msg -%}
    You can only choose the 'match_merge' incremental_strategy when file_format is set to 'parquet'
  {%- endset %}

  {% if file_format not in ['parquet'] %}
    {% do exceptions.raise_compiler_error(invalid_file_format_msg) %}
  {% endif %}
{% endmacro %}

{#
macro for validating file_format in case of merge
#}
{% macro dbt_spark_validate_merge(file_format) %}
  {% set invalid_file_format_msg -%}
    You can only choose the 'merge' incremental_strategy when file_format is set to 'delta'
  {%- endset %}

  {% if file_format not in ['delta'] %}
    {% do exceptions.raise_compiler_error(invalid_file_format_msg) %}
  {% endif %}
{% endmacro %}
