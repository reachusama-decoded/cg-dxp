-- AUTHOR: choose the declared ETF offering population and preserve source identity.
-- This parseable placeholder deliberately fails the population contract.
select product_id, fund_name as product_name, vehicle, share_class, ticker,
       asset_class, category, currency, source_layer, source_id, source_url
from {{ ref('cg_products') }}
where 1 = 0
