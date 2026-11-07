-- assert_nav_within_tolerance: singular test that fails when the calculated
-- NAV-per-unit drifts more than 1 basis point from the custodian-reported
-- NAV-per-unit. A singular test returning ANY rows is a failure, and
-- `dbt build` will not run downstream models past a failed test on an upstream
-- mart. Threshold is 1bp = 0.0001 fractional, expressed in bps as 1.0.

with calc as (
    select fund_id, position_date, calc_nav_per_unit
    from {{ ref('fct_portfolio_returns') }}
    where calc_nav_per_unit is not null
),

custodian as (
    -- In production this reads the custodian NAV feed; for the reference build
    -- the seed below stands in.
    select fund_id, position_date, nav_per_unit
    from {{ ref('seed_custodian_nav') }}
),

variance as (
    select
        c.fund_id,
        c.position_date,
        c.calc_nav_per_unit,
        cu.nav_per_unit                                          as custodian_nav,
        (c.calc_nav_per_unit - cu.nav_per_unit) / cu.nav_per_unit * 10000.0
            as variance_bps
    from calc c
    inner join custodian cu
        on cu.fund_id = c.fund_id
        and cu.position_date = c.position_date
)

select *
from variance
where abs(variance_bps) > 1.0
