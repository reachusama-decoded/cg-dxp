-- Source-aligned product · Client & advisor system. Faithful pass-through of the
-- atlas.advisors extract, one row per advisor, landed unchanged so dom_party__advisor has
-- a typed table to conform.
select *
from {{ source('atlas', 'advisors') }}
