{{ config(materialized='incremental', unique_key='event_id', incremental_strategy='delete+insert') }}
select event_id, fund_id, cast(market_value as decimal(18,2)) as market_value
from {{ ref('arrivals') }}
