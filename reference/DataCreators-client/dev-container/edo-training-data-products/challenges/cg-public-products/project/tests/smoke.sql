-- Only the neutral smoke result is assessed by this public environment test.
{{ config(tags=['smoke']) }}
select * from {{ ref('cg_environment_smoke') }}
where seed_rows != 2 or seed_sum != 3 or run_nonce = 'NOT_RUN'
