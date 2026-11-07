# Cohort 7 — Day 3 (Wednesday): dbt practical, Martin's platform session, recap

Source: `extracts/cohort7/d3-transcript.txt`, `d3-ai-notes.txt`, `d3-agenda.txt`.

## As delivered

| Time | What happened |
|---|---|
| 09:00 | "Do you see the 02 folder in challenges? That's your job today." Self-paced `challenges/02-dbt-pipeline` (v1): reading plus authoring sections, Phase 1 sources and staging (about an hour), Phase 2 intermediate, marts, tests, docs, capstone mart. Martin at 11:00. Break reminder around 10:00. |
| 09:00–11:00 | Learners work; instructors circulate. (The transcript here is mostly room chatter; a helicopter-ride story.) |
| 11:00 | Martin (platform team), recorded for the guide: Airflow and Astronomer, Databricks and Unity Catalog, access, data contracts, the vended data products repo, blueprints, DAB, compute. About an hour with questions. |
| 12:00 | Lunch. |
| 13:00 | Back to the challenges. |
| 14:00 | Recap: "what did we learn?" (below). Volunteers assigned for Thursday morning: bitemporal loading (columns and one or two strategies) and Harness/CI-CD. |
| 14:10 | End. |

## Martin's platform session — the content (reuse where a guest is not available)

**Airflow at CG today:** about 12,000 live DAGs (15,000 total, many switched off) on one open-source Airflow 2.11 instance over a huge EKS cluster (hundreds of thousands of CPUs available), with noisy-neighbour problems (one DAG can take hundreds or thousands of Spark executors). Astronomer told them the biggest sensible instance is about 2,000 DAGs. Options considered: many EKS clusters each with its own Airflow (lots of management), AWS MWAA (weak scaling, Celery only, no DR story for tier-one data), Astronomer (chosen: they built an interim DR plugin for 15-minute RPO / two-hour RTO, now managed DR; largest open-source contributor; good support; a CLI that runs everything locally; quick deployments). Today teams get an Airflow vended through DevOps templates, with an opinionated repo that favours Databricks. The migration is a "messy middle" over months or years: net-new jobs go to Astro now; critical pipelines move last. Airflow 2.11 is end of life (extended support to April), so vended instances are Airflow 3.3 with the new UI; learners will live in the Airflow UI, not the Astro UI (which is for platform operations). Astro executor (Celery-based, being rewritten in Rust) instead of the Kubernetes executor.

**Cross-team dependencies:** Airflow assets (publish an asset, downstream DAGs subscribe); across many Airflows a CG plugin ("Scaffy") reads published assets and pushes them to Confluent Kafka via centrally managed secrets, so no Airflow API tokens are shared; a system-lineage UI shows which job consumes which assets (not a data lineage tool). AutoSys still exists; integration both ways by API.

**Operations:** onboarding to ops with a criticality level, a warranty period and knowledge transfer; Datadog dashboards are auto-vended per Airflow instance (Databricks metrics to follow); non-production Airflow instances hibernate outside business hours (tell platform if you have offshore teams); health-check DAGs are vended but cost money; cost reports from Airflow's new cost endpoint; Cloudability not soon. Teams own their platform now (patching, vulnerabilities); monthly release notes; a Catalyst skill updates your repo from the copier template (review the PR because you will have customised things).

**Databricks and Unity Catalog:** seven years of Databricks, started on Azure with a hive metastore (no sharing). Unity Catalog: data lives outside the workspace and is bound to workspaces; all one Unity per region. Three catalog types: application catalogs (one per workspace; your scratch pad and the jump point to publishing), source-aligned catalog (one; ingestion-like, minimal translation; some teams such as CEDA already publish straight into it), domain catalogs (where curation happens; holds domain data and consumer-aligned data). Four kinds of data, three catalog types. Access: schema-level access via AD groups is automated; table-level access is supported manually (architecture sign-off exists); attribute-level (ABAC) later. Application catalogs cannot be shared: write to your application catalog, a vended blueprint copies to the domain catalog after data quality rules run; that keeps tiering (the platform is tier one), DQ and access standard. DR rules will be the data creator's to write (managed DR in preview).

**Contracts and the repo:** contracts follow ODCS (Open Data Contract Standard) and ODPS, as YAML, including access; a contract is required to publish to a domain catalog; contracts seed the Marketplace, which is the discovery layer; a CI/CD check that the contract exists and conforms is coming. "datacounsel" converts a contract to DDL for Flyway migrations (Martin would rather drop Flyway and deploy from the contract). The vended repo: dot files (linters, pre-commit, mise), `data_products/` (blueprints such as `dag_exec_check` and the Databricks run-now blueprint; clusters and pools; shared assets such as dbt models), `iac/`, plugins, tests. A data product is a Databricks Asset Bundle plus a dbt project with datasets; inside a dataset folder sit the dbt, the Airflow YAML (Astro blueprints: "write YAML, the blueprint turns it into a DAG") and the DAB job YAML (the lines that run dbt commands). An Airflow task only triggers a Databricks job; Databricks runs the SQL. Serverless compute is preferred (classic compute spins up EC2 and needs warm-up; endpoints are whitelisted). Consumer workspaces for business users are being designed.

## Recap at 14:00 (the facts Michael pulled from the room)

dbt pipelines can do most of the work; 80–90% of the code can be generated from a good contract; the code lives in the EDO data products repo under `data_products/` ("if you run the capstone in the wrong folder on Friday, that's on you"); Airflow blueprints are filled with YAML; Databricks only runs Spark, so dbt SQL is translated to Spark; data on S3 is in Delta format by default (columnar; logs and manifests give ACID; you can insert and delete rows, unlike plain Parquet); three Unity Catalog types; data quality tests are easy to add; materialisation can be configured in the project file and inside the model file.

## Issues seen

- A learner still lacked GitHub access to the training repo on Wednesday (needs the GitHub team; BSP contact).
- The day is long on unstructured practical time; the instructor plan's pair "test review" did not happen.
