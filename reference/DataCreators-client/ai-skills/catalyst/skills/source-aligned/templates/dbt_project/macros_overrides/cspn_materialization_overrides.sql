{#
    Upsert strategy changes for parquet data in incremental materialization
#}
{% materialization incremental, adapter='databricks', supported_languages=['sql', 'python'] -%}
  -- Validate early so we don't run SQL if the file_format is invalid --
  {%- set raw_file_format = config.get('file_format', default='parquet') -%}
  {%- set raw_strategy = config.get('incremental_strategy') or 'insert_overwrite' -%}
  {%- set file_format = dbt_spark_validate_get_file_format(raw_file_format) -%}
  -- Validate early so we don't run SQL if the strategy is invalid --
  {% set strategy = dbt_spark_validate_get_incremental_strategy(raw_strategy, file_format) -%}


  {%- set unique_key = config.get('unique_key', none) -%}
  {%- set load_type = config.get('load_type', 'incremental') -%}
  {%- set app_cycle_date = cspn_runtime_app_cycle_date() -%}
  {%- set partition_by = config.get('partition_by', none) -%}

  {%- set full_refresh_mode = (flags.FULL_REFRESH == True) -%}

  {% set target_relation = this %}
  {% set existing_relation = load_relation(this) %}
  {% set tmp_relation = make_temp_relation(this) %}

  {% if strategy == 'merge' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_merge(file_format) %}
  {% endif %}

  {% if strategy == 'delete_merge' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_merge(file_format) %}
  {% endif %}

  {% if strategy == 'upsert' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_upsert(file_format) %}
  {% endif %}

  {% if strategy in ['match_merge','match_merge_reference','match_merge_alt_v2'] %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_match_merge(file_format) %}
  {% endif %}

  {% if strategy == 'match_merge_v2' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_match_merge(file_format) %}
  {% endif %}

  {% if strategy == 'bitemporal_load' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_bitemporal_load(file_format) %}
  {% endif %}

  {% if strategy == 'bitemporal_load_v2' %}
    {%- set unique_key = config.require('unique_key') -%}
    {% do dbt_spark_validate_bitemporal_load(file_format) %}
  {% endif %}

  {% if strategy == 'insert_overwrite' and partition_by %}
    {% call statement() %}
      set spark.sql.sources.partitionOverwriteMode = DYNAMIC
    {% endcall %}
  {% endif %}

  {{ run_hooks(pre_hooks) }}

  {% if existing_relation is none %}
    {% set build_sql = create_table_as(False, target_relation, sql) %}
  {% elif existing_relation.is_view or full_refresh_mode %}
    {% do adapter.drop_relation(existing_relation) %}
    {% set build_sql = create_table_as(False, target_relation, sql) %}
  {% else %}
    {% do run_query(create_table_as(True, tmp_relation, sql)) %}
    {% set build_sql = dbt_spark_get_incremental_sql(strategy, tmp_relation, target_relation, unique_key, app_cycle_date, load_type) %}
  {% endif %}

{% if strategy not in ['upsert', 'scd2', 'bitemporal_load', 'bitemporal_load_v2', 'match_merge','match_merge_alt_v2', 'match_merge_v2', 'delete_merge', 'match_merge_reference'] %}
  {%- call statement('main') -%}
     {{ build_sql }}
  {%- endcall -%}
  {%else%}
    {% set upsert_query_steps = build_sql %}
    {% if upsert_query_steps is string  %}
        {%- call statement('main') -%}
           {{ upsert_query_steps }}
        {%- endcall -%}
     {%else%}
        {% set main_called = [] %}
        {% for step in upsert_query_steps %}
            {% if step is string and (step | trim) %}
              {% call statement('main') %}{{ step }}{% endcall %}
              {% do main_called.append(1) %}
            {% else %}
              {% do log("Skipping empty SQL step from strategy=" ~ strategy ~ ", model=" ~ this, info=true) %}
            {% endif %}
          {% endfor %}
        {# When all steps are empty, fall back or raise a clear error.
           Empty steps usually mean the Caspian extension macros are not
           installed in this dbt project (the upstream cspn_extension.*
           macros return empty strings as stubs). Without intervention,
           dbt would later raise the cryptic
           "Compilation Error: Model X did not produce any statements"
           which hides the root cause from operators. #}
        {% if main_called | length == 0 %}
          {% if var('allow_cspn_local_fallback', false) %}
            {% do log("No SQL steps executed for strategy=" ~ strategy ~ ", model=" ~ this ~ ". Local fallback: running no-op.", info=true) %}
            {%- call statement('main') -%} SELECT 1 {%- endcall -%}
          {% else %}
            {% do exceptions.raise_compiler_error(
              "Strategy '" ~ strategy ~ "' on model " ~ this ~ " returned no executable SQL steps. " ~
              "This usually means the Caspian extension macros are not installed (the cspn_extension.* macros return empty stubs in this project). " ~
              "Either install the Caspian extension package, or set `vars: { allow_cspn_local_fallback: true }` in dbt_project.yml to run a no-op SELECT 1 for local development."
            ) %}
          {% endif %}
        {% endif %}
     {%endif%}
  {%endif%}


  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}

{%- endmaterialization %}
