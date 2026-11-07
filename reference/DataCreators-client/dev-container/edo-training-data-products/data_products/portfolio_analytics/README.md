# Portfolio Analytics Airflow

Assigned v2 practice uses [Airflow Portfolio Analytics](../../challenges/v2/airflow/README.md) and its copied Python DAG starter.

This native product remains the v1 platform reference. Its guide is
[`../../challenges/v1/03-airflow-orchestration/README.md`](../../challenges/v1/03-airflow-orchestration/README.md).

The native product combines dbt, Airflow, runbook and monitoring examples. Its production-style service promises are illustrative; they do not establish that the training fixture is a deployed service.

The compatible `calc_nav_per_unit` field means holdings-only GBP exposure divided by 100 million synthetic units, excluding cash. Display it as holdings value per synthetic unit. Neither its historical fixture comparison nor its name establishes official fund/share-class NAV or custodian-published share-price reconciliation.

## Verify

From the challenge folder:

```bash
bash verify.sh
```

The challenge verify script checks DAG import health and the expected
Airflow/Cosmos structure against this product tree.
