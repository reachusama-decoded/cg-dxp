# RCA — Airflow silently boots with blank Databricks settings when started from the wrong shell

| Field | Value |
|---|---|
| **Date** | 2026-08-03 |
| **Status** | Documented + guide fixed on `feature/improvements`; container behaviour left deliberately loud (see §6) |
| **Severity** | High — makes Challenge 03 look broken; the DAG fails to import at all, with an error that points nowhere near the cause |
| **Components** | `docker-compose.override.yml` (env interpolation) · `.mise/env.sh` · `data_products/portfolio_analytics/dbt/profiles.yml` · Astro CLI / Docker Compose |
| **Discovered while** | Running a beginner trainee agent through Challenge 03; user independently reported the same suspicion from day-to-day use |
| **Related** | `docs/rca/2026-08-03-dbt-databricks-auth-hang.md` (same empty-vs-unset failure class) |

---

## 1. Summary

If `astro dev start` is run from a shell that does **not** have the Databricks environment variables
loaded, the Airflow containers come up with those variables **set to the empty string** — not unset,
*empty*. Airflow then fails to import the DAG entirely, with:

```
Credentials in profile "portfolio_analytics", target "dev" invalid:
  Invalid catalog name : ``.
```

The empty backticks are the whole story: dbt was handed a catalog name of `""`.

This confirms a suspicion reported from practice: *"sometimes I have a shell where the DBT env vars
are not defined, and I think that breaks Airflow if I start it on that same shell; if I spin up a new
shell the env vars get populated and I can restart it."* That is exactly right, and the mechanism is
now proven below.

The especially nasty part: `dbt` keeps working perfectly in your devcontainer terminal the entire
time. The containers captured a bad environment **at boot**, so fixing your shell afterwards changes
nothing until you restart them.

---

## 2. Proof

**Step 1 — the containers really do have empty values** (not missing ones):

```console
$ docker exec edo-training_06858d-scheduler-1 env | grep -E '^DBT_|^DATABRICKS_'
DATABRICKS_CONFIG_FILE=/home/astro/.databrickscfg
DATABRICKS_HOST=
DATABRICKS_HTTP_PATH=
DBT_CATALOG=
DBT_SCHEMA=
```

**Step 2 — where the empties come from.** `docker-compose.override.yml` forwards host env into the
containers using Compose interpolation with an empty fallback:

```yaml
    DATABRICKS_HOST: "${DATABRICKS_HOST:-}"
    DATABRICKS_HTTP_PATH: "${DATABRICKS_HTTP_PATH:-}"
    DBT_SCHEMA: "${DBT_SCHEMA:-}"
    DBT_CATALOG: "${DBT_CATALOG:-}"
```

`${VAR:-}` means "use `$VAR`, or the empty string if it is unset or empty". Compose resolves this
against the shell that invoked `astro dev start`. So a shell missing the variables does not omit
them — it **defines them as empty** inside every Airflow container.

**Step 3 — why an empty value is worse than a missing one.** The dbt profile supplies defaults:

```yaml
      catalog: "{{ env_var('DBT_CATALOG', 'training_dev') }}"
      schema: "{{ env_var('DBT_SCHEMA', 'training_student') }}"
```

dbt's `env_var(name, default)` returns `default` **only when the variable is unset**. A set-but-empty
variable resolves to `""`, silently bypassing the default. Hence `Invalid catalog name : ``.`

The override file's own comment shows this was not the intent:

> *"Without these the DAG falls back to `training_student`."*

It does not fall back. `${DBT_SCHEMA:-}` guarantees the fallback can never fire.

**Step 4 — a correctly-initialised shell has the values.** Run inside the repo, where mise's
`hook-env` has evaluated `.mise/env.sh`:

```console
DATABRICKS_HOST                        https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com
DATABRICKS_HTTP_PATH                   /sql/1.0/warehouses/267dd55b7f7395ce
DBT_CATALOG                            training_dev
DBT_SCHEMA                             training_gqp
AIRFLOW_VAR_DATABRICKS_JOB_PREFIX      [dev gqp]
```

**Step 5 — restarting from that shell fixes it.**

```console
$ astro dev restart --wait 5m
$ docker exec edo-training_06858d-scheduler-1 env | grep -E '^DBT_|^DATABRICKS_HOST'
DATABRICKS_HOST=https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/267dd55b7f7395ce
DBT_CATALOG=training_dev
DBT_SCHEMA=training_gqp

$ astro dev run dags list-import-errors
No data found
```

Everything downstream then works: the Cosmos task group renders all 14 dbt tasks, the freshness gate
task test succeeds, and `mise run challenge:verify 03` passes.

---

## 3. Why a shell can be missing the variables

The values are not in `.env` and are not baked into the image. They reach your shell only through
mise, and mise's environment is **directory-scoped and hook-driven**:

- `.mise/env.sh` is evaluated by `mise activate`'s `hook-env`, which fires on the shell prompt when
  your working directory is inside the trusted repo. A shell sitting outside the repo, a
  non-interactive shell, or a shell opened before `mise trust`/first-run setup completed will not
  have them.
- Part of the contract comes from `/etc/profile.d/dbt-env.sh`, written by `clone-sources`. On this
  machine that file is **absent**, so anything depending on it contributes nothing.
- `mise run setup:databricks` is what populates the underlying config in the first place; a shell
  opened before that ran has nothing to load.

Any of these produces a shell where `DBT_CATALOG` is simply not there — and Compose turns "not there"
into `""` at container boot.

---

## 4. Symptoms cheat-sheet

| What you see | What it means |
|---|---|
| `astro dev run dags list-import-errors` non-empty, ending in ``Invalid catalog name : ``.`` | Containers booted without the env. Restart from a good shell. |
| `dbt debug` in your terminal says **All checks passed**, but Airflow tasks fail with credential errors | Classic boot-time capture mismatch. Your shell is fine; the containers are not. |
| Freshness gate or dbt tasks fail with a connection / `http_path` error | Same root cause, different surface. |
| DAG runs but writes to `training_student` instead of `training_<you>` | A partially-populated environment at boot. |

**Fix, every time:**

```bash
mise run setup:databricks     # only if you have not authenticated yet
astro dev restart --wait 5m   # from a terminal whose cwd is the repo root
astro dev run dags list-import-errors   # expect: No data found
```

**Prevention:** always run `mise run setup:databricks` **before** `astro dev start`, and start the
stack from a fresh terminal opened at the repo root.

---

## 5. Quick self-check before starting Airflow

Run this in the shell you are about to start Astro from. Anything that prints `SET-BUT-EMPTY` or
`UNSET` means: open a new terminal at the repo root first.

```bash
for v in DATABRICKS_HOST DATABRICKS_HTTP_PATH DBT_CATALOG DBT_SCHEMA; do
  eval "val=\$$v"
  if   [ -z "${val+x}" ]; then s="UNSET"
  elif [ -z "$val" ];    then s="SET-BUT-EMPTY"
  else                        s="$val"; fi
  printf '%-24s %s\n' "$v" "$s"
done
```

---

## 6. Why the container behaviour was left as-is

The tempting fix is to give the Compose interpolations real defaults:

```yaml
    DBT_CATALOG: "${DBT_CATALOG:-training_dev}"
    DBT_SCHEMA: "${DBT_SCHEMA:-training_student}"
```

That was deliberately **not** done. It would convert a loud failure into a silent one: the DAG would
import happily and then read and write `training_student` — someone else's schema — instead of the
trainee's own. A cold-started stack failing to import is unpleasant but honest; a cold-started stack
quietly operating on the wrong schema is a data-correctness problem that could go unnoticed for a
long time.

`DATABRICKS_HOST` and `DATABRICKS_HTTP_PATH` have no safe defaults at all — they are per-workspace.

The chosen remedy is therefore **detection and documentation**, not a fallback:

- The Challenge 03 prerequisites now quote the exact `Invalid catalog name : ``.` error, explain that
  the containers captured the environment at boot, and state that a working terminal `dbt` does not
  mean a working Airflow.
- `.devcontainer/TROUBLESHOOTING.md` carries the same symptom → cause → fix entry.
- This RCA records the mechanism and the self-check.

If this recurs often enough to warrant it, the right next step is a **preflight in the `astro dev
start` path** that refuses to boot when any of the four variables is unset or empty — failing before
the containers exist, rather than minutes later inside a Cosmos traceback.

---

## 7. Lessons

1. **`${VAR:-}` in Compose is not a pass-through; it is an assignment to empty.** To forward a
   variable only when it exists, list the bare key (`- DBT_CATALOG`) instead of mapping it to an
   interpolated default.
2. **Empty is not unset — and this repo has now been bitten by that three times.** The auth hang
   (`DBT_ACCESS_TOKEN=""`), the profile sentinel work, and now this. `.mise/env.sh` already
   normalises empty→unset for tokens; the same discipline needs to extend to anything crossing into
   a container.
3. **Boot-time environment capture breaks the usual debugging instinct.** "It works in my terminal"
   is not evidence about a long-running container that snapshotted its environment minutes or hours
   ago.
4. **Trust the practitioner's hunch, then prove it.** The reported pattern — bad shell breaks it, new
   shell plus restart fixes it — was exactly correct, and took four commands to confirm once someone
   looked.
