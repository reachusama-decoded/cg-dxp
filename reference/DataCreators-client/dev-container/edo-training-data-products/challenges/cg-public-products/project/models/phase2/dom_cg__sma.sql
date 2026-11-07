-- AUTHOR SMA domain. One row per offering/strategy in its declared scope.
select product_id, fund_name as product_name, vehicle, share_class, asset_class,
       category, currency, source_id as product_source_id, source_url as product_source_url,
       cast(null as decimal(12,4)) as net_expense_bps,
       cast(null as date) as fee_as_of_date, cast(null as string) as fee_source_id,
       cast(null as string) as fee_source_url
from {{ ref('cg_products') }} where 1=0
