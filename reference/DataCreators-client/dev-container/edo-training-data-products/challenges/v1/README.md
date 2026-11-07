# Training Challenges

A guided path from a working devcontainer to a real CG data product. Do them in order.

**Prerequisite:** open this repo in its devcontainer and run `mise run setup:databricks`
once (mints your Databricks auth for every challenge — no per-challenge setup).

| # | Folder | You learn | You author |
|---|--------|-----------|------------|
| 00 | `00-environment-check` | your toolchain is ready | (nothing — run the check) |
| 01 | `01-docker-intro` | build & run a container on the devcontainer's Docker | the Dockerfile under `starter/` |
| 02 | `02-dbt-pipeline` | a `source → staging → marts` dbt pipeline on Databricks | the dbt model bodies |
| 03 | `03-airflow-orchestration` | orchestrate that pipeline with Airflow + Cosmos | the DAG (`data_products/portfolio_analytics`) |
| 04 | `04-atlas-capstone` | build a real paved-path data product | the source→domain→consumer dbt models (`data_products/atlas_elt`) |

**Run any challenge:** `mise run challenge:verify <NN>` (e.g. `mise run challenge:verify 02`).
**Start over (02-04):** `mise run challenge:reset <NN>` re-blanks the files you author back to stubs.

Challenges 03 and 04 keep their real artifacts under `data_products/` with real product
names (`portfolio_analytics`, `atlas_elt`); each such folder's `README.md` header points
back to its `challenges/NN-*` guide.

---

*Maintaining these challenges?* See [`CHANGES.md`](CHANGES.md) for what we changed from
the original ported challenges and why.
