-- AUTHOR integration: complete spine, scalar selected evidence, review/criterion semantics.
select *, cast(null as decimal(12,6)) as return_3y_pct,
       cast(null as string) as return_basis, cast(null as string) as return_kind,
       cast(null as string) as return_period, cast(null as string) as return_as_of_date,
       cast(null as string) as return_source_id, cast(null as string) as criterion_status,
       cast(null as string) as comparison_status, cast(null as string) as reason_code
from {{ ref('dom_cg__etf') }} where 1=0
