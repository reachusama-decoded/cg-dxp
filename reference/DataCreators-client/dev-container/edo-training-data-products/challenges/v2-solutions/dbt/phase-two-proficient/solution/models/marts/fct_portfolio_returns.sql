-- fct_portfolio_returns: the published daily-grain fact.
-- One row per (fund_id, position_date, instrument_id). `fct_` is the fact-table
-- prefix; consumers are the RM dashboard, compliance, and the client app API.
with holdings as (
    select * from {{ ref('int_holdings_enriched') }}
),

funds as (
    select * from {{ ref('int_fund_attributes') }}
),

fund_mv as (
    -- Total base-ccy market value per fund per day — the numerator for NAV.
    select
        fund_id,
        position_date,
        sum(mv_base_ccy) as total_mv_base
    from holdings
    group by 1, 2
),

with_units as (
    -- units_outstanding is synthesised here for the reference build; a real feed
    -- ships it alongside holdings. calc_nav_per_unit = total MV / units.
    select
        fund_mv.fund_id,
        fund_mv.position_date,
        fund_mv.total_mv_base,
        100000000.0 as units_outstanding
    from fund_mv
)

select
    h.fund_id,
    h.position_date,
    h.instrument_id,
    f.fund_name,
    h.quantity,
    h.mv_local_ccy,
    h.local_ccy,
    h.fx_rate_to_base,
    h.mv_base_ccy,
    u.total_mv_base / u.units_outstanding as calc_nav_per_unit
from holdings h
left join with_units u
    on u.fund_id = h.fund_id
    and u.position_date = h.position_date
left join funds f
    on f.fund_id = h.fund_id
