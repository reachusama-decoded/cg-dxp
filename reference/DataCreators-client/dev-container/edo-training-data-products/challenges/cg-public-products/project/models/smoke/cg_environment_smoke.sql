-- Supplied neutral environment check. It contains no capstone transformation answer.
{{ config(tags=['smoke']) }}
select count(*) as seed_rows,
       sum(cast(value as integer)) as seed_sum,
       '{{ var("run_nonce") }}' as run_nonce
from {{ ref('cg_smoke') }}
