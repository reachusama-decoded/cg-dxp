-- The associate dimension loaded bitemporally. Each run loads one batch (var 'batch'): the
-- full file for a business date, or a corrected re-delivery of the same business date.
{{ config(
    materialized='incremental',
    incremental_strategy='bitemporal_load',
    bitemporal_key='associate_id'
) }}

with batch as (
    select associate_id, name, job_code, job_title, tenure_months, business_date
    from {{ ref('associate_feed') }}
    where batch_id = '{{ var("batch") }}'
)

select
    associate_id,
    name,
    job_code,
    job_title,
    tenure_months,
    md5(concat_ws('|', name, job_code, job_title, tenure_months))  as dl_row_hash,
    cast(business_date as date)                                    as dl_business_start_dt,
    cast(null as date)                                             as dl_business_end_dt,
    cast(now() as timestamp)                                       as dl_system_start_ts,
    cast(null as timestamp)                                        as dl_system_end_ts,
    true                                                           as dl_current_ind
from batch
