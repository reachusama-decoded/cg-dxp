{#
 query for truncating target table
#}
{%macro exec_truncate(target)%}
{{ generate_trunc_query(target.schema,target.include(schema=false)) }}
{%endmacro%}

{#
 query for inserting data into target table from temp table for upsert
 #}
{%macro exec_upsert(target,temp_db,temp_table)%}
{{generate_upsert_query(target.schema, target.include(schema=false), temp_db, temp_table)}}
{%endmacro%}

{#
 query for inserting data into target table from temp table for upsert
 #}
{%macro exec_match_merge(target,temp_db,temp_table)%}
{{generate_upsert_query(target.schema, target.include(schema=false), temp_db, temp_table)}}
{%endmacro%}

{%macro get_match_merge_sql(target, source, unique_key, temp_db, temp_table, domain, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
  {% if 'audit_column_list' in config.model.config.extra.get('meta', {}) %}
    {% set audit_cols = config.model.config.extra.get('meta')['audit_column_list'] %}
  {% else %}
    {% set audit_cols = var('audit_col_list', []) %}
  {% endif %}

{{ generate_match_merge_temp_tbl_query(dest_cols_list,target,audit_cols,domain,source,unique_key,temp_db,temp_table) }}
{%endmacro%}

{%macro get_match_merge_sql_v2(target, source, unique_key, temp_db, temp_table, domain, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
  {% if 'audit_column_list' in config.model.config.extra.get('meta', {}) %}
    {% set audit_cols = config.model.config.extra.get('meta')['audit_column_list'] %}
  {% else %}
    {% set audit_cols = var('audit_col_list', []) %}
  {% endif %}

{{ generate_match_merge_temp_tbl_query_v2(dest_cols_list,target,audit_cols,domain,source,unique_key,temp_db,temp_table) }}
{%endmacro%}

{%macro get_match_merge_reference_sql(target, source, unique_key, temp_db, temp_table, domain, app_cycle_date, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
  {% if 'audit_column_list' in config.model.config.extra.get('meta', {}) %}
    {% set audit_cols = config.model.config.extra.get('meta')['audit_column_list'] %}
  {% else %}
    {% set audit_cols = var('audit_col_list', []) %}
  {% endif %}

{{ generate_match_merge_reference_temp_tbl_query(dest_cols_list,target,audit_cols,domain,source,unique_key,temp_db,temp_table,app_cycle_date) }}
{%endmacro%}

{%macro get_match_merge_alt_v2_sql(target, source, unique_key, temp_db, temp_table, domain, action_code_col=none, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
  {% if 'audit_column_list' in config.model.config.extra.get('meta', {}) %}
    {% set audit_cols = config.model.config.extra.get('meta')['audit_column_list'] %}
  {% else %}
    {% set audit_cols = var('audit_col_list', []) %}
  {% endif %}

{{ generate_match_merge_alt_v2_temp_tbl_query(dest_cols_list,target,audit_cols,domain,source,unique_key,temp_db,temp_table,action_code_col) }}
{%endmacro%}

{%macro get_delete_merge_sql(target, source, unique_key)%}
{{ generate_delete_merge_temp_tbl_query(target, source, unique_key) }}
{%endmacro%}

{%macro get_expire_merge_master_bitemporal_expire_sql(target, source, unique_key, curr_timestamp)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_expire_merge_master_bitemporal_expire_query(dest_cols_list, target, audit_cols, source.include(schema=false), unique_key, curr_timestamp) }}
{%endmacro%}

{%macro get_expire_merge_master_bitemporal_merge_sql(target, source, unique_key, action_code_col, curr_timestamp, dest_columns=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_expire_merge_master_bitemporal_merge_query(dest_cols_list, target, audit_cols, source.include(schema=false), unique_key, curr_timestamp, action_code_col) }}
{%endmacro%}

{#
 get the create temp table statement for upsert
#}
{%macro get_upsert_sql(target, source, unique_key, temp_db, temp_table,dest_columns, predicates=none)%}
    {%- set dest_columns = adapter.get_columns_in_relation(target) -%}
   {%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
   {{ generate_temp_tbl_query(dest_cols_list,target,source.include(schema=false),unique_key,temp_db,temp_table) }}
{%endmacro%}

{%macro get_upsert_scd2_sql(target, source, unique_key, temp_db, temp_table, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{% if 'audit_column_list' in config.model.config.extra.get('meta') %}
{% set audit_cols = config.model.config.extra.get('meta')['audit_column_list'] %}
{% else %}
  {% set audit_cols = var('audit_col_list', []) %}
{%endif%}
{{ generate_scd2_temp_tbl_query(dest_cols_list,target, audit_cols, source.include(schema=false),unique_key,temp_db,temp_table) }}
{%endmacro%}

{%macro get_merge_scd2_sql(target, source, unique_key, dest_columns=none, predicates=none)%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_scd2_merge_query(dest_cols_list,target, audit_cols, source.include(schema=false),unique_key) }}
{%endmacro%}

{%macro get_merge_master_bitemporal_sql(target, source, unique_key, action_code_col, curr_timestamp, start_date_col, end_date_col, dest_columns=none, bitemporal_col_version='v1')%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{%- if start_date_col is none -%}
  {{ generate_bitemporal_merge_query(dest_cols_list, target, audit_cols, source.include(schema=false), unique_key, curr_timestamp, action_code_col, bitemporal_col_version) }}
{%- else -%}
  {{ generate_bitemporal_merge_using_source_date_query(dest_cols_list, target, audit_cols, source, unique_key, curr_timestamp, action_code_col, start_date_col, end_date_col, bitemporal_col_version) }}
{%- endif -%}
{%endmacro%}

{%macro get_merge_bitemporal_full_expire_sql(target, source, unique_key, curr_timestamp, bitemporal_col_version='v1')%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_bitemporal_merge_expire_query(dest_cols_list,target, audit_cols, source, unique_key, curr_timestamp, bitemporal_col_version) }}
{%endmacro%}

{%macro get_merge_balance_bitemporal_full_expire_sql(target, source, unique_key, curr_timestamp, bitemporal_col_version='v1')%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_balance_bitemporal_merge_expire_query(dest_cols_list,target, audit_cols, source.include(schema=false),unique_key, curr_timestamp, bitemporal_col_version) }}
{%endmacro%}

{%macro get_merge_balance_bitemporal_sql(target, source, unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, dest_columns=none, bitemporal_col_version='v1')%}
{%- set dest_columns = adapter.get_columns_in_relation(target) -%}
{%- set dest_cols_list = dest_columns  |  map(attribute="name")| list -%}
{%- set audit_cols = config.model.config.extra.get('meta')['audit_column_list']%}
{{ generate_balance_bitemporal_merge_query(dest_cols_list,target, audit_cols, source.include(schema=false),unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, bitemporal_col_version) }}
{%endmacro%}

{% macro check_empty_src(source) %}
  {% if execute %}
    {% set rec_chk_qry %}
           SELECT * from {{ source }} LIMIT 1
    {% endset %}
    {{ dbt_utils.log_info( ("query: ",rec_chk_qry) )}}
    {% set res_chk_qry = run_query(rec_chk_qry) %}
    {% set src_row_cnt = res_chk_qry |length %}
    {{ dbt_utils.log_info( ("source row count: ",src_row_cnt) )}}
    {% if src_row_cnt > 0 %}
        {{return(1)}}
    {% else %}
        {{ dbt_utils.log_info( ("source has zero rows") )}}
        {{return(0)}}
    {%- endif %}
  {% endif %}
{%- endmacro %}

{% macro get_incremental_bitemporal_load_v2_sql(arg_dict) %}
  {% set target = arg_dict.get('target_relation') %}
  {% set source = arg_dict.get('temp_relation') %}
  {% set unique_key = arg_dict.get('unique_key') %}
  {% set load_type = config.get('load_type', 'full') %}
  {% set app_cycle_date = cspn_runtime_app_cycle_date() %}

  {# Keep this entrypoint for dbt compatibility, but delegate strategy generation
     through the shared dbt_spark_get_incremental_sql path (same pattern as EMR). #}
  {% set strategy_sql = dbt_spark_get_incremental_sql(
    'bitemporal_load_v2',
    source,
    target,
    unique_key,
    app_cycle_date,
    load_type
  ) %}

  {% if strategy_sql is string %}
    {{ return(strategy_sql) }}
  {% endif %}

  {{ return(strategy_sql | join(';' ~ '\n')) }}
{% endmacro %}

{#
 Added upsert & upsert_scd2 strategy for parquet data
#}
{%macro dbt_spark_get_incremental_sql(strategy, source, target, unique_key, app_cycle_date, load_type=None)%}
  {%- if strategy == 'append' -%}
    {{ get_insert_into_sql(source, target) }}
  {%- elif strategy == 'insert_overwrite' -%}
    {{ get_insert_overwrite_sql(source, target) }}
  {%- elif strategy == 'scd2' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {% if file_format == 'parquet'%}
      {%set sql_list = [] %}
      {% set cache_tgt_sql = " cache table "~target ~ " "%}
      {% set cache_src_sql = " cache table "~source.include(schema=false) ~""%}
      {%set drop_temp_table = "drop table if exists "~temp_db~"."~temp_table %}
      {%do sql_list.append(cache_tgt_sql) %}
      {%do sql_list.append(cache_src_sql) %}
      {%do sql_list.append(drop_temp_table) %}
      {%do sql_list.append(get_upsert_scd2_sql(target, source, unique_key, temp_db, temp_table, dest_columns=none, predicates=none).strip()) %}
      {%do sql_list.append(exec_upsert(target,temp_db,temp_table).strip())  %}
      {{return(sql_list)}}
    {%else%}
      {{ get_merge_scd2_sql(target, source, unique_key, dest_columns=none, predicates=none) }}
    {%endif%}
  {%- elif strategy == 'bitemporal_load' and load_type == 'incremental'  -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {%set start_date_col  = config.get('start_date_col', none) %}
    {%set end_date_col  = config.get('end_date_col', none) %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%do sql_list.append(get_merge_master_bitemporal_sql(target, source, unique_key, action_code_col, curr_timestamp, start_date_col, end_date_col, dest_columns=none).strip()) %}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load' and load_type == 'full' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {%set start_date_col  = config.get('start_date_col', none) %}
    {%set end_date_col  = config.get('end_date_col', none) %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%set action_code_col  = config.get('action_code_col', none) %}
      {% if check_empty_src(source) == 1 %}
         {%do sql_list.append(get_merge_bitemporal_full_expire_sql(target, source, unique_key, curr_timestamp).strip()) %}
         {%do sql_list.append(get_merge_master_bitemporal_sql(target, source, unique_key, action_code_col, curr_timestamp, start_date_col, end_date_col, dest_columns=none).strip())  %}
      {%endif%}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load' and load_type == 'expire_merge_master' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%set action_code_col  = config.get('action_code_col', none) %}
      {% if check_empty_src(source) == 1 %}
         {%do sql_list.append(get_expire_merge_master_bitemporal_expire_sql(target, source, unique_key, curr_timestamp).strip()) %}
         {%do sql_list.append(get_expire_merge_master_bitemporal_merge_sql(target, source, unique_key, action_code_col, curr_timestamp, dest_columns=none).strip())  %}
      {%endif%}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load_v2' and load_type == 'incremental'  -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {%set start_date_col  = config.get('start_date_col', none) %}
    {%set end_date_col  = config.get('end_date_col', none) %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%do sql_list.append(get_merge_master_bitemporal_sql(target, source, unique_key, action_code_col, curr_timestamp, start_date_col, end_date_col, dest_columns=none, bitemporal_col_version='v2').strip()) %}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load_v2' and load_type == 'full' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {%set start_date_col  = config.get('start_date_col', none) %}
    {%set end_date_col  = config.get('end_date_col', none) %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%set action_code_col  = config.get('action_code_col', none) %}
      {% if check_empty_src(source) == 1 %}
         {%do sql_list.append(get_merge_bitemporal_full_expire_sql(target, source, unique_key, curr_timestamp, bitemporal_col_version='v2').strip()) %}
         {%do sql_list.append(get_merge_master_bitemporal_sql(target, source, unique_key, action_code_col, curr_timestamp, start_date_col, end_date_col, dest_columns=none, bitemporal_col_version='v2').strip())  %}
      {%endif%}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load' and load_type == 'balance'  -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {%set as_of_col  = config.get('as_of_col') %}
    {%set detect_change_flag  = config.get('detect_change_flag', none) %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%do sql_list.append(get_merge_balance_bitemporal_sql(target, source, unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, dest_columns=none).strip()) %}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load_v2' and load_type == 'balance'  -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {%set as_of_col  = config.get('as_of_col') %}
    {%set detect_change_flag  = config.get('detect_change_flag', none) %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {%do sql_list.append(get_merge_balance_bitemporal_sql(target, source, unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, dest_columns=none, bitemporal_col_version='v2').strip()) %}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'bitemporal_load_v2' and load_type == 'balance_full'  -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {%set as_of_col  = config.get('as_of_col') %}
    {%set detect_change_flag  = config.get('detect_change_flag', none) %}
    {%set curr_timestamp = modules.datetime.datetime.now() %}
    {% if file_format == 'delta'%}
      {%set sql_list = [] %}
      {% if check_empty_src(source) == 1 %}
        {%do sql_list.append(get_merge_balance_bitemporal_full_expire_sql(target, source, unique_key, curr_timestamp, bitemporal_col_version='v2').strip()) %}
        {%do sql_list.append(get_merge_balance_bitemporal_sql(target, source, unique_key, curr_timestamp, as_of_col, detect_change_flag, action_code_col, dest_columns=none, bitemporal_col_version='v2').strip()) %}
      {%endif%}
      {{return(sql_list)}}
    {%endif%}
  {%- elif strategy == 'upsert' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = "temp_"~generate_uuid__temp_tbl().strip()%}
    {%set sql_list = [] %}
    {%do sql_list.append(get_upsert_sql(target, source, unique_key, temp_db, temp_table, dest_columns=none, predicates=none).strip()) %}
    {%do sql_list.append(exec_upsert(target,temp_db,temp_table).strip())  %}
    {{return(sql_list)}}

  {%- elif strategy == 'match_merge' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set domain = config.model.meta.get('domain') %}
    {%set file_format  = config.get('file_format') %}
    {% if file_format == 'parquet'%}
      {%set sql_list = [] %}
      {% set cache_tgt_sql = " cache table "~target ~ " "%}
      {% set cache_src_sql = " cache table "~source ~ " "%}
      {%do sql_list.append(cache_tgt_sql) %}
      {%do sql_list.append(cache_src_sql) %}

      {%do sql_list.append(get_match_merge_sql(target, source, unique_key, temp_db, temp_table, domain, dest_columns=none, predicates=none).strip()) %}
      {%do sql_list.append(exec_match_merge(target,temp_db,temp_table).strip())  %}
      {{return(sql_list)}}
      {%endif%}
  {%- elif strategy == 'match_merge_reference' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set domain = config.model.meta.get('domain') %}
    {%set file_format  = config.get('file_format') %}
    {% if file_format == 'parquet'%}
      {%set sql_list = [] %}
      {% set cache_tgt_sql = " cache table "~target ~ " "%}
      {% set cache_src_sql = " cache table "~source ~ " "%}
      {%do sql_list.append(cache_tgt_sql) %}
      {%do sql_list.append(cache_src_sql) %}

      {%do sql_list.append(get_match_merge_reference_sql(target, source, unique_key, temp_db, temp_table, domain, app_cycle_date, dest_columns=none, predicates=none).strip()) %}
      {%do sql_list.append(exec_match_merge(target,temp_db,temp_table).strip())  %}
      {{return(sql_list)}}
      {%endif%}
  {%- elif strategy == 'match_merge_alt_v2' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set domain = config.model.meta.get('domain') %}
    {%set file_format  = config.get('file_format') %}
    {%set action_code_col  = config.get('action_code_col', none) %}
    {% if file_format == 'parquet'%}
      {%set sql_list = [] %}
      {% set cache_tgt_sql = " cache table "~target ~ " "%}
      {% set cache_src_sql = " cache table "~source ~ " "%}
      {%do sql_list.append(cache_tgt_sql) %}
      {%do sql_list.append(cache_src_sql) %}

      {%do sql_list.append(get_match_merge_alt_v2_sql(target, source, unique_key, temp_db, temp_table, domain, action_code_col, dest_columns=none, predicates=none).strip()) %}
      {%do sql_list.append(exec_match_merge(target,temp_db,temp_table).strip())  %}
      {{return(sql_list)}}
      {%endif%}
  {%- elif strategy == 'delete_merge' -%}
    {#-- merge all columns with databricks delta - schema changes are handled for us #}
    {%set file_format  = config.get('file_format') %}
    {%set sql_list = [] %}
    {%do sql_list.append(get_delete_merge_sql(target, source, unique_key)) %}
    {%do sql_list.append(get_merge_sql(target, source, unique_key, dest_columns=none, predicates=none))  %}
    {{return(sql_list)}}
  {%- elif strategy == 'match_merge_v2' -%}
    {%set temp_db = var('temp_db')  %}
    {%set temp_table = target.include(schema=false)~"_temp" %}
    {%set domain = config.model.meta.get('domain') %}
    {%set file_format  = config.get('file_format') %}
    {% if file_format == 'parquet'%}
      {%set sql_list = [] %}
      {% set cache_tgt_sql = " cache table "~target ~ " "%}
      {% set cache_src_sql = " cache table "~source ~ " "%}
      {%do sql_list.append(cache_tgt_sql) %}
      {%do sql_list.append(cache_src_sql) %}

      {%do sql_list.append(get_match_merge_sql_v2(target, source, unique_key, temp_db, temp_table, domain, dest_columns=none, predicates=none).strip()) %}
      {%do sql_list.append(exec_match_merge(target,temp_db,temp_table).strip())  %}
      {{return(sql_list)}}
      {%endif%}
  {%- else -%}
    {#-- merge all columns with databricks delta - schema changes are handled for us #}
    {{ get_merge_sql(target, source, unique_key, dest_columns=none, predicates=none) }}
  {%- endif -%}

{%endmacro%}