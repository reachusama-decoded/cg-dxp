# Data Creators training project

Use [Getting started](GETTING_STARTED.md) for the training container, authentication and assigned v2 practice. Portfolio Analytics uses dbt-databricks and Astro; the [CG capstone](challenges/cg-public-products/README.md) uses a distinct public-product snapshot. The active task descriptions are in [challenges/v2](challenges/v2/README.md).

## Prepare for practice

Open this repository in the training dev container. Complete interactive authentication before recording evidence:

```bash
mise run setup:databricks
dpc-check
```

Read each readiness result. Resolve failed or warning gates with the instructor before the affected activity. Offline tests check local configuration and authoring support; they do not establish warehouse access or successful scheduled execution:

```bash
pytest tests/local_env/offline
```

From this project root, prepare a new dbt attempt:

```bash
mise run challenge:v2:list
mise run challenge:v2:prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
```

Preparation refuses an existing destination. Use the owning phase’s commands and profile inside the copied attempt. [Shared setup](challenges/v2/runtime/portfolio/SETUP.md) covers the supplied fixtures, approved namespace, unique relation prefix, Astro staging and evidence checks. The advanced phases have independent entry baselines.

## Project contents

- `challenges/v2/`: assigned phases, optional routes and supplied starters.
- `scripts/challenge-v2.py` and `.mise.toml`: preparation, discovery and verification tasks.
- `data_products/`: platform product examples and staged worker-visible attempts.
- `Dockerfile`, `requirements.txt` and `packages.txt`: Astro image and dependencies.
- `plugins/`: custom Airflow extensions.
- `.airflow/airflow_settings.yaml.example`: secret-free settings template; generated `airflow_settings.yaml` remains local.

The retained [v1 challenges](challenges/v1/README.md) and platform examples have their own contracts. Follow the v2 phase guide for assigned work rather than combining setup routes.

## Local Astro services

Complete Databricks setup before starting Astro from this project root:

```bash
astro dev start
astro dev logs
# Stop the services when finished:
astro dev stop
```

Use the address and login shown by the prepared runtime; VS Code port forwarding may change the browser address. Check the actual service and DAG identity. An open UI is not evidence of a successful run.

If Astro started with missing environment values, fix setup in a fresh terminal and restart the services conditionally:

```bash
astro dev restart --wait 5m
```

The assigned DAG writes evidence after quality checks. Infrastructure provisioning, product publication and deployment are separate platform responsibilities.

## Support

Use the [container troubleshooting guide](.devcontainer/TROUBLESHOOTING.md) with the failed command, selected executable, target and non-secret error. The Caspian Platform Team maintains the platform template: [support channel](https://teams.microsoft.com/l/channel/19%3Ae2680301eab549e9acdb12152fa690de%40thread.tacv2/Caspian%20C4E%20Support?groupId=17f9ec8b-6777-41fd-83f8-e505bd401595&tenantId=41b8c056-2dc3-438d-99ee-61e00287adfe).
