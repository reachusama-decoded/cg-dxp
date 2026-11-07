{% snapshot fund_history %}
{{ config(strategy='check', unique_key='fund_cd', check_cols=['fund_name','base_ccy','strategy_code','is_active']) }}
select * from {{ ref('fund_master_raw') }}
{% endsnapshot %}
