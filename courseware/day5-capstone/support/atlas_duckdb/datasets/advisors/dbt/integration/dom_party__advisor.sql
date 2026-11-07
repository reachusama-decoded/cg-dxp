-- Domain-aligned product · Party domain. The canonical advisor, one row per advisor. Trims
-- text fields and drops non-positive ids. The conformed advisor every portfolio/advisor
-- consumer mart joins to.
select
  advisor_id,
  trim(name) as name,
  trim(region) as region
from {{ ref('src_crm__advisors') }}
where advisor_id > 0
