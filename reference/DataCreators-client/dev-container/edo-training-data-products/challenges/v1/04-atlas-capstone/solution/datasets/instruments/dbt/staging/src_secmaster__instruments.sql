-- Source-aligned product · Security master. Faithful pass-through of the atlas.instruments
-- extract, one row per instrument, landed unchanged so dom_instrument__instrument has a
-- typed table to conform.
select *
from {{ source('atlas', 'instruments') }}
