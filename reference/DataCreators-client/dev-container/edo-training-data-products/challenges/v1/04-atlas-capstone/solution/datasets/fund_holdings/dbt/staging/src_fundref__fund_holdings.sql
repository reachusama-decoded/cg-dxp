-- Source-aligned product · Fund reference system. Faithful pass-through of the
-- atlas.fund_holdings extract, one row per fund/instrument holding, landed unchanged so
-- dom_fund__holding has a typed table to conform.
select *
from {{ source('atlas', 'fund_holdings') }}
