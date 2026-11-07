{#
  Custom incremental strategy: bitemporal_load.

  dbt looks for a macro named get_incremental_<strategy>_sql when a model names a strategy
  the adapter does not know. The model's SELECT is written to a temporary relation (the
  incoming batch); this macro decides how it lands in the target table.

  Two clocks on every row:
    business time  dl_business_start_dt .. dl_business_end_dt   when the fact was true
    system time    dl_system_start_ts  .. dl_system_end_ts      when the warehouse believed it
  plus dl_current_ind (true = open in both clocks) and dl_row_hash (hash of the tracked
  columns, for change detection). Nothing is ever updated in place except closing a system
  interval: every change is a new row, which is what makes "as was" answerable.

  Per business key (config bitemporal_key), for each incoming row:
    new key                              -> insert, current
    same hash as the current version     -> nothing (no change)
    different hash, later business date  -> close the old row's SYSTEM clock, re-insert it
                                            with its BUSINESS clock ended (we still believe
                                            it for its own dates), insert the new version
    different hash, same business date   -> a correction: close the old row's SYSTEM clock,
                                            insert the corrected row for the same dates
#}
{% macro get_incremental_bitemporal_load_sql(arg_dict) %}
  {%- set target = arg_dict["target_relation"] -%}
  {%- set source = arg_dict["temp_relation"] -%}
  {%- set key = config.require('bitemporal_key') -%}
  {%- set cols = arg_dict["dest_columns"] | map(attribute='name') | list -%}

  {#- 1. close the system clock of every current row that the batch changes -#}
  {%- set close_sql -%}
    update {{ target }} as t
    set dl_system_end_ts = s.dl_system_start_ts,
        dl_current_ind   = false
    from {{ source }} as s
    where t.{{ key }} = s.{{ key }}
      and t.dl_current_ind
      and t.dl_row_hash <> s.dl_row_hash
  {%- endset -%}
  {% do run_query(close_sql) %}

  {#- 2. carry forward the superseded business versions with their business clock ended -#}
  {%- set carry_sql -%}
    insert into {{ target }} ({{ cols | join(', ') }})
    select
      {%- for c in cols %}
        {%- if c == 'dl_business_end_dt' %} cast(s.dl_business_start_dt - interval 1 day as date)
        {%- elif c == 'dl_system_start_ts' %} s.dl_system_start_ts
        {%- elif c == 'dl_system_end_ts' %} cast(null as timestamp)
        {%- elif c == 'dl_current_ind' %} false
        {%- else %} t.{{ c }}
        {%- endif %}{{ "," if not loop.last }}
      {%- endfor %}
    from {{ target }} as t
    join {{ source }} as s
      on s.{{ key }} = t.{{ key }}
     and t.dl_system_end_ts = s.dl_system_start_ts
     and s.dl_business_start_dt > t.dl_business_start_dt
  {%- endset -%}
  {% do run_query(carry_sql) %}

  {#- 3. insert the incoming rows that are new keys or changed versions -#}
  insert into {{ target }} ({{ cols | join(', ') }})
  select {{ cols | join(', ') }}
  from {{ source }} as s
  where not exists (
      select 1 from {{ target }} as t
      where t.{{ key }} = s.{{ key }}
        and t.dl_current_ind
        and t.dl_row_hash = s.dl_row_hash
  )
{% endmacro %}
