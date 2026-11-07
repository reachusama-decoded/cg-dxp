{% macro cspn_hello() -%}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is not none %}
      {{ extn.cspn_hello(run_query) }}
    {% endif %}
  {% endif %}
{%- endmacro %}


{% macro cspn_sys_standard_table_fields( model ) -%}
     cast( concat_ws('-', year__, month__, day__) as date)                     as cspn_file_date
   , concat_ws('/', year__ , lpad(month__, 2, '0'), lpad(day__, 2, '0'), time__) as cspn_file_load_order
{%- endmacro %}


{% macro caspian_extn_or_none() -%}
  {% set caspian_mod = modules.get('caspian') %}
  {% if caspian_mod is not none %}
    {{ return(caspian_mod.dbt_extn) }}
  {% endif %}

  {% if var('allow_cspn_local_fallback', false) %}
    {{ return(none) }}
  {% endif %}

  {{ exceptions.raise_compiler_error(
    "Expected Caspian python extension to be injected. " ~
    "Run in Caspian runtime or pass --vars '{allow_cspn_local_fallback: true}'."
  ) }}
{%- endmacro %}


{% macro _cspn_extn_required() -%}
  {{ return(caspian_extn_or_none()) }}
{%- endmacro %}


{% macro cspn_runtime_run_id() -%}
  {% set run_id = var('run_id', none) %}
  {% if run_id is none or (run_id | string | trim) == '' %}
    {% set run_id = invocation_id %}
  {% endif %}
  {{ return(run_id | string) }}
{%- endmacro %}


{% macro cspn_runtime_app_cycle_date() -%}
  {% set app_cycle_date = var('app_cycle_date', none) %}
  {% if app_cycle_date is none or (app_cycle_date | string | trim) == '' %}
    {% if run_started_at is not none %}
      {% set app_cycle_date = run_started_at.strftime('%Y-%m-%d') %}
    {% else %}
      {% set app_cycle_date = modules.datetime.datetime.utcnow().strftime('%Y-%m-%d') %}
    {% endif %}
  {% endif %}
  {{ return(app_cycle_date | string) }}
{%- endmacro %}


{% macro cspn_checkpoint_table_name() -%}
  {% set checkpoint_table = var('checkpoint_table', '') | string | trim %}
  {% if not checkpoint_table and target is defined and target.database is defined and target.schema is defined %}
    {% set checkpoint_table = target.database ~ '.' ~ target.schema ~ '.standard_dataset_checkpoints' %}
  {% endif %}
  {{ return(checkpoint_table) }}
{%- endmacro %}


{% macro cspn_standard_source_table_load_filter(src) -%}
  {% set table_partition = var('table_partition', none) %}
  {% if table_partition is string and (table_partition | trim) == '' %}
    {% set table_partition = none %}
  {% endif %}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is not none %}
      {% set checkpoint_table = cspn_checkpoint_table_name() %}
      {% if checkpoint_table and extn.cspn_apply_checkpoint_schema_override is defined %}
        {% do extn.cspn_apply_checkpoint_schema_override(checkpoint_table) %}
      {% endif %}
      {% set filter_clause = extn.cspn_standard_source_table_load_filter(run_query, config, src, table_partition) %}
    {% else %}
      {# extn is none only when allow_cspn_local_fallback=true (otherwise caspian_extn_or_none raises) #}
      {% set allow_fallback = var('allow_cspn_local_fallback', false) %}
      {% if not allow_fallback %}
        {{ exceptions.raise_compiler_error(
          "Caspian module not injected (unexpected extn=None) and allow_cspn_local_fallback is false. "
          ~ "Refusing to continue."
        ) }}
      {% endif %}

      {% do log(
        "Caspian module not injected; local fallback enabled (1=1). "
        ~ "This is for LOCAL TESTING ONLY. Model=" ~ this ~ ", target=" ~ target.name,
        info=true
      ) %}
      {% set filter_clause = "1 = 1" %}
    {% endif %}
  {% else %}
    {% set filter_clause = "1 = 2" %}
  {% endif %}
  {{ filter_clause }}
{%- endmacro %}


{% macro cspn_source(source_name, table_name=None, source_table_name=None) -%}
  {#
    Supports both call patterns:
      1) cspn_source(source_name, table_name)
      2) cspn_source(source_catalog, source_schema, source_table)
  #}
  {% if source_table_name is none %}
    {%- set src = source(source_name, table_name) -%}
    {{ return(src ~ " WHERE " ~ cspn_standard_source_table_load_filter(src)) }}
  {% else %}
    {%- set src = api.Relation.create(database=source_name, schema=table_name, identifier=source_table_name) -%}
    {%- if execute -%}
      {%- set filter_clause = cspn_standard_source_table_load_filter(src) -%}
    {%- else -%}
      {%- set filter_clause = "1 = 2" -%}
    {%- endif -%}
    {{ return("(select * from " ~ src ~ " where " ~ filter_clause ~ ")") }}
  {% endif %}
{%- endmacro %}


{% macro cspn_commit_checkpoints() -%}
  {% set run_id = cspn_runtime_run_id() %}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is none %}{{ return("") }}{% endif %}
    {% set checkpoint_table = cspn_checkpoint_table_name() %}
    {% if checkpoint_table and extn.cspn_apply_checkpoint_schema_override is defined %}
      {% do extn.cspn_apply_checkpoint_schema_override(checkpoint_table) %}
    {% endif %}
    {{ return(extn.cspn_commit_checkpoints(run_query, config, run_id)) }}
  {% endif %}
  {{ return("") }}
{%- endmacro %}



{% macro get_audit_cols() -%}
  {% set default_audit_col_list = var('audit_col_list', none) %}
  {% if default_audit_col_list is none or (default_audit_col_list is string and (default_audit_col_list | trim) == '') %}
    {% set default_audit_col_list = config.model.meta.get('audit_column_list', []) %}
  {% endif %}
  {% if default_audit_col_list is string %}
    {% set default_audit_col_list = [default_audit_col_list] %}
  {% endif %}
  {% set run_id = cspn_runtime_run_id() %}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is none %}
      {% set exprs = [] %}
      {% for c in default_audit_col_list %}
        {% do exprs.append("cast(null as string) as " ~ c) %}
      {% endfor %}
      {{ return(exprs | join(", ")) }}
    {% endif %}
    {{ return(extn.cspn_audit_columns(config, default_audit_col_list, run_id)) }}
  {% endif %}
  {{ return(default_audit_col_list | join(", ")) }}
{%- endmacro %}


{% macro generate_surrogate_key() -%}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% set cols = extn.cspn_surrogate_key(config) if extn is not none else ['Key'] %}
  {% else %}
    {% set cols = ['Key'] %}
  {% endif %}
  {{ dbt_utils.surrogate_key(cols) }} as cspn_id_key
{%- endmacro %}


{% macro generate_surrogate_key_v2() -%}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% set cols = extn.cspn_surrogate_key(config) if extn is not none else ['Key'] %}
  {% else %}
    {% set cols = ['Key'] %}
  {% endif %}
  {{ dbt_utils.surrogate_key(cols) }} as dlrowuid
{%- endmacro %}


{% macro generate_surrogate_key_v3() -%}
  {% if execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is none %}
      {% set cols = config.get('meta', {}).get('surrogate_key_cols', ['Key']) %}
    {% else %}
      {% set cols = extn.cspn_surrogate_key(config) %}
    {% endif %}
  {% else %}
    {% set cols = ['Key'] %}
  {% endif %}
  {{ dbt_utils.surrogate_key(cols) }} as dl_row_uid
{%- endmacro %}


{% macro fetch_upsert_cols(dest_col_list) %}
  {% set extn = caspian_extn_or_none() %}
  {% if extn is not none %}
    {{ extn.cspn_get_upsert_columns_dbt(dest_col_list) }}
  {% endif %}
{%- endmacro %}


{% macro generate_uuid__temp_tbl() %}
  {% set extn = caspian_extn_or_none() %}
  {% if extn is not none %}
    {{ extn.cspn_get_uuid() }}
  {% endif %}
{% endmacro %}


{% macro generate_temp_tbl_query(columns,target,source,unique_key,temp_db,temp_table) %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_temp_tbl_query(columns, target, source, unique_key, temp_db, temp_table) }}
{%endmacro%}


{%macro generate_trunc_query(schema,table)%}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_trunc_query(schema, table) }}
{%endmacro%}


{%macro generate_upsert_query(schema, table, temp_db, temp_table)%}
  {% if execute %}
    {% set extn = _cspn_extn_required() %}
    {% if extn is none %}{{ return("") }}{% endif %}
    {{ extn.cspn_generate_upsert_query(run_query, schema, table, temp_db, temp_table, config) }}
  {% endif %}
{%endmacro%}


{% macro cspn_delete_app_cycle_data(table) -%}
  {% set existing_relation = load_relation(table) %}
  {% if existing_relation is not none and execute %}
    {% set extn = caspian_extn_or_none() %}
    {% if extn is not none %}
      {{ extn.cspn_delete_app_cycle_data(run_query, table, cspn_runtime_app_cycle_date()) }}
    {% endif %}
  {% endif %}
{%- endmacro %}


{% macro generate_scd2_temp_tbl_query(columns, target, audit_cols, source, unique_key, temp_db, temp_table) %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set run_id = cspn_runtime_run_id() %}
  {{ extn.cspn_generate_scd2_temp_tbl_query(columns, target, audit_cols, source, unique_key, temp_db, temp_table, app_cycle_date, run_id) }}
{%endmacro%}

{% macro generate_scd2_merge_query(columns,target, audit_cols, source,unique_key) %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}
  {{ extn.cspn_generate_scd2_merge_query(columns, target, audit_cols, source, unique_key, app_cycle_date) }}
{%endmacro%}

{% macro generate_bitemporal_merge_query(columns,target, audit_cols, source,unique_key, curr_timestamp, action_code_col, bitemporal_col_version='v1') %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set app_cycle_prior_day = appcyclepriorglobalbusinessdate(app_cycle_date) %}
  {{ dbt_utils.log_info( ("app_cycle_prior_day in bi-temporal merge query is : ",app_cycle_prior_day) ) }}
  {{ extn.cspn_generate_bitemporal_merge_query(columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, action_code_col, bitemporal_col_version) }}
{%endmacro%}

{% macro generate_bitemporal_merge_using_source_date_query(columns,target, audit_cols, source,unique_key, curr_timestamp, action_code_col, start_date_col, end_date_col, bitemporal_col_version='v1') %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_bitemporal_merge_using_source_date_sql(columns, target, audit_cols, source, unique_key, curr_timestamp, action_code_col, start_date_col, end_date_col, bitemporal_col_version) }}
{%endmacro%}

{% macro generate_bitemporal_merge_expire_query(columns,target, audit_cols, source,unique_key, curr_timestamp, bitemporal_col_version='v1') %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set app_cycle_prior_day = appcyclepriorglobalbusinessdate(app_cycle_date) %}
  {{ dbt_utils.log_info( ("app_cycle_prior_day in full merge expire is : ",app_cycle_prior_day) ) }}
  {{ extn.cspn_generate_bitemporal_update_expire_rows(target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version) }}
{%endmacro%}

{% macro generate_balance_bitemporal_merge_expire_query(columns,target, audit_cols, source,unique_key, curr_timestamp, bitemporal_col_version='v1') %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set app_cycle_prior_day = appcyclepriorglobalbusinessdate(app_cycle_date) %}
  {{ dbt_utils.log_info( ("app_cycle_prior_day in full merge expire is : ",app_cycle_prior_day) ) }}
  {{ extn.cspn_generate_balance_bitemporal_update_expire_rows(target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version) }}
{%endmacro%}

{% macro generate_expire_merge_master_bitemporal_expire_query(columns, target, audit_cols, source,unique_key, curr_timestamp)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set system_app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set app_cycle_date = appcycleglobalbusinessdate(system_app_cycle_date) %}
  {% set app_cycle_prior_day = appcyclepriorglobalbusinessdate(app_cycle_date) %}
  {{ dbt_utils.log_info( ("app_cycle_prior_day in expire merge is : ",app_cycle_prior_day) ) }}
  {{ extn.cspn_generate_expire_merge_master_bitemporal_expire_query(target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp) }}
{%endmacro%}

{% macro generate_expire_merge_master_bitemporal_merge_query(columns,target, audit_cols, source,unique_key, curr_timestamp, action_code_col) %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {% set system_app_cycle_date = cspn_runtime_app_cycle_date() %}
  {% set app_cycle_date = appcycleglobalbusinessdate(system_app_cycle_date) %}
  {% set app_cycle_prior_day = appcyclepriorglobalbusinessdate(app_cycle_date) %}
  {{ dbt_utils.log_info( ("app_cycle_prior_day in bi-temporal expire merge query is : ",app_cycle_prior_day) ) }}
  {{ extn.cspn_generate_expire_merge_master_bitemporal_merge_query(columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, action_code_col) }}
{%endmacro%}

{% macro generate_balance_bitemporal_merge_query(columns,target, audit_cols, source,unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, bitemporal_col_version='v1') %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_balance_bitemporal_merge_query(columns, target, audit_cols, source, unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, bitemporal_col_version) }}
{%endmacro%}

{% macro generate_match_merge_temp_tbl_query(dest_cols_list,target, audit_cols, domain, source,unique_key,temp_db,temp_table)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_match_merge_temp_tbl_query(dest_cols_list, target, audit_cols, domain, source, unique_key, temp_db, temp_table) }}
{%endmacro%}

{% macro generate_match_merge_reference_temp_tbl_query(dest_cols_list,target, audit_cols, domain, source,unique_key,temp_db,temp_table,app_cycle_date)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_match_merge_reference_temp_tbl_query(dest_cols_list, target, audit_cols, domain, source, unique_key, temp_db, temp_table, app_cycle_date) }}
{%endmacro%}

{% macro generate_match_merge_alt_v2_temp_tbl_query(dest_cols_list,target, audit_cols, domain, source,unique_key,temp_db,temp_table, action_code_col)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_match_merge_alt_v2_temp_tbl_query(dest_cols_list, target, audit_cols, domain, source, unique_key, temp_db, temp_table, action_code_col) }}
{%endmacro%}

{% macro generate_match_merge_temp_tbl_query_v2(dest_cols_list,target, audit_cols, domain, source,unique_key,temp_db,temp_table)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_match_merge_temp_tbl_query_v2(dest_cols_list, target, audit_cols, domain, source, unique_key, temp_db, temp_table) }}
{%endmacro%}

{% macro generate_delete_merge_temp_tbl_query(target, source, unique_key)  %}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.cspn_generate_delete_merge_temp_tbl_query(target, source, unique_key) }}
{%endmacro%}


{% macro create_curr_table_and_load_temp_table(trgt_schema, trgt_relation) %}
  {%set temp_db = var('temp_db') %}
  {%set temp_table = trgt_relation.include(schema=false)~"_temp" %}
  {%set sql_list = [] %}
  {%set create_final_table = create_table_as(False, trgt_relation, sql) %}
  {%set insert_temp_table = "INSERT INTO TABLE "~temp_db~"."~temp_table~" SELECT * FROM "~trgt_schema~"."~trgt_relation.include(schema=false) %}
  {%do sql_list.append(create_final_table) %}
  {%do sql_list.append(insert_temp_table) %}
  {{return(sql_list)}}
{%- endmacro %}


{% macro generate_match_merge_sql_through_post_hook(tmp_relation, strategy, target_table, unique_key) %}
  {% set trgt_schema = target.schema %}
  {% set target_relation = api.Relation.create(schema=trgt_schema, identifier=target_table) %}
  {% set existing_relation = load_relation(target_relation) %}

  {{ dbt_utils.log_info( ("generating match merge for: ",target_relation)  )}}
  {{ dbt_utils.log_info( ("target_schema: ",trgt_schema) )}}
  {{ dbt_utils.log_info( target_relation.include(schema=false) )}}
  {{ dbt_utils.log_info( ("existing_relation: ",existing_relation) )}}

  {% if existing_relation is none %}
    {% set build_sql = create_curr_table_and_load_temp_table(trgt_schema, target_relation) %}
  {% else %}
    {% set build_sql = dbt_spark_get_incremental_sql(strategy, tmp_relation, target_relation, unique_key) %}
  {% endif %}

  {{ dbt_utils.log_info( ("build_sql: ",build_sql) )}}

  {% if strategy not in ['upsert', 'scd2','bitemporal_load', 'match_merge','match_merge_alt','match_merge_alt_v2','match_merge_reference','delete_merge'] %}
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
          {%for step in upsert_query_steps %}
              {%- call statement('main') -%}
              {{step}}
              {%-endcall -%}
             {%endfor%}
       {%endif%}
    {%endif%}

{%- endmacro %}

{% macro add_default_metric(temporary_db) -%}
  {% set extn = _cspn_extn_required() %}
  {% if extn is none %}{{ return("") }}{% endif %}
  {{ extn.add_default_metric(temporary_db) }}
{%- endmacro %}

{% macro appcyclepriorglobalbusinessdate(app_cycle_date) -%}
  {% set dleffectivedate = app_cycle_date |string %}
  {% set calendar_table = var('calendar_table', 'cg_calendar_v4') %}
  {% set calendar_schema = var('calendar_schema', 'curated_ref') %}
  {% set calendar_catalog = var('calendar_catalog', 'caspian_dev1') %}
  {% set priorcalendardate_query %}
    select distinct prior_calendar_date
      from {{ calendar_catalog }}.{{calendar_schema}}.{{calendar_table}}
     where calendar_date = cast('{{dleffectivedate}}' as date)
  {% endset %}
  {% set priorcalendardt = run_query(priorcalendardate_query) %}
  {% if execute %}
    {% if priorcalendardt |length == 0 %}
      {{ exceptions.raise_compiler_error("Not a valid date " ~ app_cycle_date ~ ". Please check cgcalendar table.") }}
    {% else %}
      {% set priorcalendar_date = priorcalendardt.columns[0].values()[0] %}
      {{ dbt_utils.log_info( ("priorcalendar_date: ", priorcalendar_date) )}}
      {{ return(priorcalendar_date) }}
    {% endif %}
  {% endif %}
{% endmacro %}


{% macro appcycleglobalbusinessdate(app_cycle_date) -%}
  {% set dleffectivedate = app_cycle_date |string %}
  {% set calendar_table = var('calendar_table', 'cg_calendar_v4') %}
  {% set calendar_schema = var('calendar_schema', 'curated_ref') %}
  {% set calendar_catalog = var('calendar_catalog', 'caspian_dev1') %}
  {% set get_global_business_date_query %}
    select CASE WHEN global_business_or_holiday_flag = 'B' 
       THEN calendar_date 
       ELSE prior_global_business_date 
           END AS APP_CYCLE_DATE
      from {{ calendar_catalog }}.{{ calendar_schema }}.{{ calendar_table }}
  where calendar_date = cast('{{dleffectivedate}}' as date)
  {% endset %}
  {% if execute %}
    {% set globalbusinessdate_result = run_query(get_global_business_date_query) %}
    {% if globalbusinessdate_result |length == 0 %}
      {{ exceptions.raise_compiler_error("Not a valid date " ~ app_cycle_date ~ ". Please check cgcalendar table.") }}
    {% else %}
      {% set globalbusiness_date = globalbusinessdate_result[0]['APP_CYCLE_DATE'] %}
	  {{ dbt_utils.log_info( ("globalbusiness_date: ", globalbusiness_date) )}}
      {{ return(globalbusiness_date) }}
    {% endif %}
  {% endif %}
{% endmacro %}