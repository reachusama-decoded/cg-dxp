-- Domain-aligned product · Party domain. The canonical client, one row per client. Trims
-- text, upper-cases the domicile code, and drops non-positive ids, so every consumer mart
-- joins to one agreed client definition rather than the raw shape of whichever system
-- produced it.
select
  client_id,
  trim(name) as name,
  trim(segment) as segment,
  upper(trim(domicile)) as domicile
from {{ ref('src_crm__clients') }}
where client_id > 0
