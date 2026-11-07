# Auth Failures — No Token or Profile — Full Fix

## Symptoms to grep for

```
No credential provider found
Could not connect to Databricks
KeyError: 'token'
~/.databrickscfg not found
dbt.exceptions.DbtRuntimeError: Could not connect
```

## Root cause

When running locally, dbt reads credentials from `~/.dbt/profiles.yml`.
When running inside a Databricks job task, there is no home directory with a
pre-configured profile. The wrapper must hydrate auth from the Databricks
secret scope or the job's environment variables.

## Diagnostic steps

1. Confirm whether the failure is on a local run or a bundle-run task.
2. For local runs: verify `~/.dbt/profiles.yml` has a valid `databricks`
   target with `token` or `oauth_client_id` populated.
3. For bundle-run tasks: inspect `dbt_wrapper.py` for `dbutils.secrets.get()`
   calls — if absent, the wrapper is not hydrating credentials.

## Fix for bundle-run tasks

In `dbt_wrapper.py`, hydrate the dbt profile's token from the secret scope.

> **Auth scope reminder (DBX-SEC-002):** the secret retrieved here MUST be a
> service-principal-scoped credential — either an OAuth-materialized bearer
> token or an SP-PAT. User PATs are forbidden in any path that creates
> database objects. The job's `run_as` identity is the SP; the token in the
> secret scope must match. See `/connect-databricks` for the OAuth-only
> pattern that avoids this fork entirely.

```python
import os
from databricks.sdk.runtime import dbutils

# Token is the SP's bearer credential — never a user PAT (DBX-SEC-002).
token = dbutils.secrets.get(scope="dbt-secrets", key="databricks-token")
os.environ["DATABRICKS_TOKEN"] = token
os.environ["DATABRICKS_HOST"] = os.environ.get(
    "DATABRICKS_HOST", "https://<workspace>.azuredatabricks.net"
)
```

Then reference environment variables in `profiles.yml`:

```yaml
databricks_profile:
  target: dev
  outputs:
    dev:
      type: databricks
      host: "{{ env_var('DATABRICKS_HOST') }}"
      http_path: /sql/1.0/warehouses/<warehouse-id>
      token: "{{ env_var('DATABRICKS_TOKEN') }}"
      schema: dev_employee
      threads: 4
```

See `/write-dbt-wrapper` for the full auth-hydration pattern.
See `/databricks-docs` for the Databricks SDK secrets API reference.
