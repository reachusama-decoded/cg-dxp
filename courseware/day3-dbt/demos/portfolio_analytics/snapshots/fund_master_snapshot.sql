{% snapshot fund_master_snapshot %}
{{ config(
    unique_key='fund_cd',
    strategy='check',
    check_cols=['fund_name', 'base_ccy', 'strategy_code', 'is_active']
) }}
-- SCD type 2 history of the fund master: every change to a checked column closes the
-- current row (dbt_valid_to) and opens a new one. Day 4's bitemporal demo builds on this.
select * from {{ source('product_ref', 'fund_master_raw') }}
{% endsnapshot %}
