-- Source-aligned product · Trading platform. Faithful pass-through of the atlas.trades
-- fact extract, one row per trade, kept in the producing system's shape (no cleaning) so
-- the domain layer has a typed, source-faithful table to conform.
-- Materialised as a table (not the default view): the 10k-row fact is read once and reused
-- by every downstream model, so a physical table avoids re-scanning the seed.
{{ config(materialized='table') }}

select *
from {{ source('atlas', 'trades') }}
