# Portfolio Analytics Airflow

This is the native `data_products/portfolio_analytics` product used by
Challenge 03. The challenge guide lives in
[`../../challenges/v1/03-airflow-orchestration/README.md`](../../challenges/v1/03-airflow-orchestration/README.md).

The product combines the portfolio-analytics dbt project with the Airflow DAGs,
runbooks, and monitoring docs that the challenge asks trainees to wire.

## Verify

From the challenge folder:

```bash
bash verify.sh
```

The challenge verify script checks DAG import health and the expected
Airflow/Cosmos structure against this product tree.
