# Getting Started

## 1. Install the Catalyst Plugin

For Catalyst activities, install the approved plugin through VS Code user settings. Follow the assigned manual route if access is unavailable.

Open **Preferences: Open User Settings (JSON)** (`Ctrl+Shift+P`) and add:

```jsonc
{
	"chat.plugins.enabled": true,
	"chat.useAgentSkills": true,
	"chat.plugins.marketplaces": [
		"https://github.com/cg-open-itg/catalyst.git"
	]
}
```

Then:

1. Reload VS Code.
2. Open Copilot Chat (`Ctrl+Shift+I`).
3. Run `/plugins`.
4. Enable **AI Catalyst**.

Notes:

- Set these in **user settings**, not workspace settings.
- No local clone is required for plugin usage.
- Official install guide: <https://github.com/cg-open-itg/catalyst/blob/main/docs/install.md>

## 2. Dev Container Setup

You'll need Docker Desktop access — request the **CPZ_INF_BB00000003_Docker_Desktop_User** role if you don't already have it.

Follow the [Dev Container README](.devcontainer/README.md#getting-started) to open the repo in the dev container, complete the automatic OAuth-first setup, and verify it with `dpc-check`.

Important first-start behavior:

- Dev container startup can take a while on first open. Be patient while setup scripts finish.
- Read `dpc-check` results in the dev-container terminal. Resolve the affected failed or warning gate before proceeding; printed output alone does not establish readiness.

If you only have a PAT, use the explicit fallback:

```bash
# Run inside the dev container
mise run setup:databricks --pat
```

After the container is up, run the verification steps (deterministic checks first):

```bash
# Fast local checks
dpc-check
pytest tests/local_env/offline
# Optional: run live integration checks (set CERT_INTEGRATION_TESTS=1 to enable)
# CERT_INTEGRATION_TESTS=1 pytest tests/local_env/live -m integration

# End-to-end Databricks gate
bash scripts/verify-with-databricks.sh

# Or run the umbrella verifier
mise run verify:local-dev
```


## Assigned v2 practice

Use [challenges/v2](challenges/v2/README.md) for the current task descriptions. Portfolio Analytics runs on dbt-databricks/Astro; the [CG capstone](challenges/cg-public-products/README.md) uses distinct product, expense and return inputs. Prepare an attempt from this project root:

```bash
mise run challenge:v2:list
mise run challenge:v2:prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
```

Prepare Airflow with tool `airflow`; its advanced work uses `phase-two-proficient`. Follow its owning phase and shared setup. For Friday, create your own CG product with `mise run challenge:cg:prepare` as described in the [CG capstone guide](challenges/cg-public-products/README.md), then follow [Your working folder](challenges/cg-public-products/project/README.md#your-working-folder) in that product. The [challenges index](challenges/README.md) lists every current route.

Assigned Airflow work authors a Python DAG in the copied starter. YAML-generated platform DAGs below are a separate reference route.

---

<details>
<summary>Platform reference: migrations, native products and deployment</summary>

These commands describe the broader platform and retained v1 product workflow. They are outside the assigned v2 preparation path and require the appropriate namespace, permissions and deployment approval.

## 3. Deploy Contracts via Flyway

Contracts (`.odcs.yaml`) define table schemas. `datacounsel generate-migration` converts them into Flyway-compatible SQL, and `flyway migrate` applies the SQL to Databricks.

- **Locally**, generated SQL goes into `.local/migrations/` (gitignored, throwaway).
- **In dev and higher environments**, CI generates SQL into the data product's `contract/migrations/` folder and commits it to the branch.

You only commit the `.odcs.yaml` contract — never the generated SQL.

### Initialize (first time only)

```bash
mise run contract:init
```

### Deploy a contract

```bash
mise run contract:migrate data_products/YOUR_PRODUCT_NAME/datasets/instruments/contract/instruments.odcs.yaml
```

### Repair a failed migration

```bash
mise run contract:repair data_products/YOUR_PRODUCT_NAME/datasets/instruments/contract/instruments.odcs.yaml
```

For more details on Flyway, external tables, and CI pipeline behavior, see the [datacounsel README](datacounsel/README.md#local-developer-workflow).

## 4. Run dbt

For these native platform products, run the dbt mise tasks from the project root with the product name. Assigned v2 direct dbt commands run inside the copied attempt.

```bash
# Install dbt package dependencies
mise run dbt:deps YOUR_PRODUCT_NAME

# Run all models for YOUR_PRODUCT_NAME
mise run dbt:run YOUR_PRODUCT_NAME

# Run only the instruments models
mise run dbt:run YOUR_PRODUCT_NAME -- --select instruments

# Test models
mise run dbt:test YOUR_PRODUCT_NAME
```

You can pass additional dbt flags after `--`.

For more on dbt configuration, targets, and credentials, see the [Dev Container README — Running DBT](.devcontainer/README.md#running-dbt) section.

## 5. Deploy the Databricks Asset Bundle

From the repo root, `cd` into your data product folder and deploy:

```bash
cd data_products/YOUR_PRODUCT_NAME
databricks bundle deploy -t local
```

Once deployed, your jobs will appear in the Databricks **Jobs & Pipelines** page, prefixed with `[dev <initials>]` — for example:

> `[dev nlsy] currency_job`

You can trigger them manually from the Databricks UI or let Airflow handle orchestration (next step).


## 6. Start Astronomer (Local Airflow)

Important: complete Databricks setup before starting Astro. Run `mise run setup:databricks` first so `AIRFLOW_VAR_DATABRICKS_JOB_PREFIX` is present when containers start.

If you started Astro before Databricks setup, rerun setup and restart Astro to reload environment variables:

```bash
mise run setup:databricks
astro dev restart --wait 5m
```

Start the local Airflow environment from the repo root:

```bash
cd /workspaces/edo-training-data-products

# Start Airflow
astro dev start

# View logs
astro dev logs

# Stop when done
astro dev stop
```

Use the address and login supplied by the running Astro environment. The UI commonly uses port 8080; VS Code forwarding can change the browser address.

If you open the UI while `astro dev start` is still building/initializing, you may briefly see an **Unauthorized** page. This is usually temporary. Wait for startup to finish, then refresh the page.

If DAG/task behavior in the UI does not match what you expect, verify you are looking at the **devcontainer** Astro environment (not a different local Astro instance):

```bash
# Run inside the devcontainer terminal
docker ps --format '{{.Names}}' | grep 'edo-training.*-scheduler-1'
```

If `run_clients_dbt` fails with `Job ID for job name clients_job can not be found`, rerun setup to restore the Databricks job prefix wiring and refresh connections, then restart Astro from inside the devcontainer:

```bash
mise run setup:databricks
astro dev restart --wait 5m
```

DAG files live in `data_products/` at the repo root, which is mounted as the Airflow dags folder.

These platform DAGs are generated from dataset YAML files, such as `datasets/currency/airflow/currency.dag.yml`. Assigned v2 practice instead authors the Python DAG supplied in its starter.

For more details on Airflow DAG configuration, connections, and troubleshooting, see the [Dev Container README — Working with Airflow DAGs](.devcontainer/README.md#working-with-airflow-dags) section.

## 7. Retained v1 challenges

The numbered `00`–`04` challenges retain their original platform workflow. Read [challenges/v1](challenges/v1/README.md) before selecting this optional route; `mise run challenge:verify <NN>` uses that historical contract.

</details>

