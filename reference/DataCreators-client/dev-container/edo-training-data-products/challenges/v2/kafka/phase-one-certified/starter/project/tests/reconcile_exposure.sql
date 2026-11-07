select 1 as failure where abs((select sum(exposure) from {{ ref('fund_exposure') }}) - 250) > 0.001
