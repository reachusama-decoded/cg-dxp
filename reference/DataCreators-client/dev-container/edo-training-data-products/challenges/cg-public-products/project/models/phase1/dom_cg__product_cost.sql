-- AUTHOR: enrich the ETF spine with the correct fee evidence, units and null dates.
-- No instructor calculation is supplied in this placeholder.
select product_id, product_name, vehicle, share_class, ticker, asset_class,
       category, currency, source_id as product_source_id, source_url as product_source_url,
       cast(null as decimal(12,6)) as net_expense_pct,
       cast(null as decimal(12,4)) as net_expense_bps,
       cast(null as date) as fee_as_of_date,
       cast(null as string) as fee_source_id,
       cast(null as string) as fee_source_url
from {{ ref('src_cg__product') }}
where 1 = 0
