-- Supplied primitive adapter: retain all components/layers, normalize numeric/date blanks.
-- Selecting the contracted component/layer and joining it correctly remains your work.
select product_id, component, cast(nullif(value_pct, '') as decimal(12,6)) as value_pct,
       date(nullif(as_of_date, '')) as as_of_date, source_field, source_layer,
       source_id, source_url, source_area
from {{ ref('cg_fees') }}
