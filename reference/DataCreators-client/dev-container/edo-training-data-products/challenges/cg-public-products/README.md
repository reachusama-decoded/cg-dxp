# CG product-information capstone

Friday's capstone. You build an internal product-information data product from a frozen snapshot of public CG fund data. Phase 1 is personal, phase 2 is paired and phase 3 is personal again.

This folder holds the instructions and the starting template. **Don't work in it.** You work in your own product folder under `data_products/`, which the shared Airflow (Astro) stack can already see.

## Before you start

You need:

- the training container open, with Databricks sign-in done (`mise run setup:databricks`, then `dpc-check`);
- from your instructor: your product folder name (`cg_public_products_<you>`), catalog, schema and table-name prefix. Don't guess these or reuse someone else's.

## Create your product

Run from the training project root, the folder containing `.mise.toml`:

```bash
mise run challenge:cg:prepare cg_public_products_YOUR_NAME --catalog YOUR_CATALOG --schema YOUR_SCHEMA --prefix YOUR_PREFIX
```

This copies [project/](project/README.md) to `data_products/cg_public_products_YOUR_NAME/` and records your assigned target in its `.capstone-workspace.json`. It never overwrites an existing product, and it refuses a prefix that another product already uses. Running it again for the same name is safe: it stops without changing anything.

Then follow [Your working folder](project/README.md#your-working-folder) in the project guide. It shows the per-terminal settings and the workspace check to run before any dbt command. Create your personal Git repository in your product folder during phase 1. The training repository ignores `data_products/cg_public_products_*/`, so your work stays in your own repository. While Airflow is running it takes ownership of product files, so Git needs `git config --global --add safe.directory "$PWD"` once in each product folder. The project guide includes this step.

## Phases

| Phase | Time | Work | Where |
|---|---|---|---|
| 0 | 09:00–09:30 | Design and readiness | Your product |
| 1 | 09:30–11:25 | Individual ETF core | Your product and personal repository |
| 2 | 11:25–14:00 | Pair integration, custom orchestration and callback, personal AI skill | The product declared for your pair |
| 3 | 14:15–15:15 | Both advanced components, individually | Your product again |
| Report | 15:15–16:00 | Report, presentation and submission | Your product |

For phase 2, your pair works in one declared product: one partner's, or a separate `cg_public_products_<pair>` folder created with the same command. For phase 3, bring the reviewed pair commit into your personal repository, keeping your own history. Run this from your product folder, replacing `PAIR_PRODUCT`:

```bash
git fetch ../PAIR_PRODUCT main
git checkout FETCH_HEAD -- .
git commit -m "Bring reviewed pair baseline $(git rev-parse --short FETCH_HEAD)"
```

Your files now match the pair baseline. Your earlier phase 1 commits stay in your history. Personal repositories and the pair product start from separate `git init` runs, so a plain `git merge` refuses to combine them. The project guide has the details for each phase.

## Template updates

Template changes reach new products only. To see which template files differ from your product, without changing anything:

```bash
mise run challenge:cg:diff cg_public_products_YOUR_NAME
```

## Running on the shared Airflow

Your product's DAGs run on the training repository's Astro stack (`mise exec -- astro dev start --wait 5m`, then `mise run databricks:oauth-refresh`). Each product's `.airflowignore` lets Airflow read only its `dags/` folder. DAG IDs start with your product folder name, so products never clash. Before each run, and again after any code change once no run is active, pin your code from the product folder:

```bash
python runtime/stage_astro.py
```

The worker refuses code that changed after pinning and any table prefix outside your assignment. To check the whole route, run `python verify-starter.py --mode connected` from your product folder. It builds the neutral smoke model on Databricks and runs your `<product>__environment_smoke` DAG on the worker.
