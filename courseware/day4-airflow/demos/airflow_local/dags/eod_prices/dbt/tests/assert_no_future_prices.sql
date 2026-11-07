-- A price dated after the vendor timestamp cannot be right.
select * from {{ ref('rpt_eod_prices_us') }}
where price_date > cast(vendor_ts as date)
