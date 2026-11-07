-- Source-aligned product · Portfolio system. Faithful pass-through of the atlas.portfolios
-- extract, one row per portfolio, landed unchanged so dom_portfolio__portfolio has a typed
-- table to conform.
select *
from {{ source('atlas', 'portfolios') }}
