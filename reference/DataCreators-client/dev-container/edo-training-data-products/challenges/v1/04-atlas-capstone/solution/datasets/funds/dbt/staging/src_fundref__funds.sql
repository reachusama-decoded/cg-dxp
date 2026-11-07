-- Source-aligned product · Fund reference system. Faithful pass-through of the atlas.funds
-- extract, one row per fund, landed unchanged so dom_fund__fund has a typed table to conform.
select *
from {{ source('atlas', 'funds') }}
