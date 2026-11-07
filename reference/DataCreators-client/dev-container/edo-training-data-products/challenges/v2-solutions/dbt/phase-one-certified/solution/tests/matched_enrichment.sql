select * from {{ ref('int_holdings_enriched') }} where fx_rate_to_base is null or close_price is null
