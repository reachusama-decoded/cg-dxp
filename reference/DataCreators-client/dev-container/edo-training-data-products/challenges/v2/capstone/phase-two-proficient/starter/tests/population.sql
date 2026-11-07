select 1 as failure where (select count(*) from {{ ref('dom_trading__trade') }}) != 9880 or (select count(*) from {{ ref('rpt_portfolio_summary') }}) != 1028
