{% snapshot portfolios_snapshot %}
{#
  SCD type-2 history for portfolios: each run compares dom_portfolio__portfolio to the
  stored rows and, when a watched column changes, closes the old record and opens
  a new one (recording validity in dbt_valid_from / dbt_valid_to). This lets you
  reconstruct the book as it stood on any past date — e.g. which advisor ran a
  portfolio last March.

  target_schema is the learner's own schema (target.schema): learners have ONE
  pre-provisioned schema and cannot create a new one, so the snapshot must land
  there rather than in a separate 'snapshots' schema.
#}
{{
  config(
    target_schema=target.schema,
    unique_key='portfolio_id',
    strategy='check',
    check_cols=['strategy', 'advisor_id']
  )
}}

select
  portfolio_id,
  advisor_id,
  strategy,
  inception_date
from {{ ref('dom_portfolio__portfolio') }}

{% endsnapshot %}
