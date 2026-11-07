-- Source-aligned product · Client & advisor system. Faithful pass-through of the
-- atlas.clients extract, one row per client, landed unchanged so dom_party__client has a
-- typed table to conform.
select *
from {{ source('atlas', 'clients') }}
