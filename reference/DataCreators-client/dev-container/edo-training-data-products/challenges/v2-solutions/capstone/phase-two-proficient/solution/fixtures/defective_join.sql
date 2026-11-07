-- Intentional defect: advisor is unrelated to the client key. Compare populations.
select pf.portfolio_id from portfolios pf join advisors a on pf.client_id = a.advisor_id where pf.portfolio_id>0
