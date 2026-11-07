---
name: troubleshoot-dbt-on-databricks
description: |
  Diagnose and resolve common dbt-on-Databricks failures: SSL/CA cert errors,
  auth failures, materialization misconfiguration, warehouse connectivity issues,
  public PyPI 404s (CG network blocks public registries), and job cold-start
  timeouts. Use when other skills emit errors or when users hit issues running
  dbt against Databricks.
  Trigger phrases: "my dbt deps failed", "dbt deps ssl error",
  "dbt task timed out", "bitemporal_load_v2 not found", "warehouse not running".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: [databricks-docs]
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012/0013 cross-ref)
    - DBX-SEC-001
    - DBX-SEC-002              # SP-PAT vs user-PAT detection in auth failures
    - SQL-DBSQL-001            # OAuth-only profiles.yml — diagnose auth failures
    # Proposed (PR 94 prose → IDs; awaiting RFD 0008)
    - DBX-SEC-003              # cgrepo Nexus mirror routing — public PyPI 404 root cause
    - DBX-SEC-005              # dbt deps CA cert handling (cgrepo SSL setup)
    - DBX-WORKFLOW-005         # Log retention on UC Volume — log-related failure diagnosis
---

# Troubleshoot dbt on Databricks

Structured failure-mode reference for dbt running against Databricks.
Match the log output against the symptom column in the table, then follow
the one-liner fix or open the linked reference for the full diagnostic walkthrough.

Consult `/databricks-docs` to look up official Databricks documentation
on any topic not covered here.

---

## When to consult this skill

Use this skill when:

- A dbt or bundle-run task exits non-zero and you need to identify the failure class quickly.
- You hit a connectivity, auth, or packaging error that is not explained by the `/run-dbt-on-databricks` or `/write-dbt-wrapper` skills.
- You want to rule out CG-network-specific causes (PyPI blocks, CA cert, secret scope misconfiguration) before escalating.

---

## Failure-Mode Table

| # | Failure | Symptom / Log Pattern | Diagnostic | Fix (one-liner) | Full reference |
|---|---|---|---|---|---|
| 1 | **dbt deps SSL / CA cert error** | `ssl.SSLCertVerificationError`; `CERTIFICATE_VERIFY_FAILED`; dbt deps exits non-zero | `grep -n "REQUESTS_CA_BUNDLE" dbt_wrapper.py` | Set `REQUESTS_CA_BUNDLE` to the CG CA bundle path in `dbt_wrapper.py` before invoking dbt | [references/failure-modes/ssl-ca-cert-error.md](references/failure-modes/ssl-ca-cert-error.md) |
| 2 | **Auth fails — no token or profile** | `No credential provider found`; `Could not connect to Databricks`; `KeyError: 'token'` | Check `dbutils.secrets.get()` calls in `dbt_wrapper.py`; confirm `~/.dbt/profiles.yml` on local runs | Hydrate `DATABRICKS_TOKEN` from `dbutils.secrets` in the wrapper for bundle-run tasks | [references/failure-modes/auth-failures.md](references/failure-modes/auth-failures.md) |
| 3 | **bitemporal_load_v2 not found** | `macro 'bitemporal_load_v2' not found`; `'bitemporal_load_v2' is undefined` | `ls macros/bitemporal_load_v2.sql`; confirm `macros/` is in the bundle `include` list | Add `macros/bitemporal_load_v2.sql` to the project and re-deploy the bundle | [references/failure-modes/bitemporal-load-v2-misconfigured.md](references/failure-modes/bitemporal-load-v2-misconfigured.md) |
| 4 | **bitemporal_load_v2 missing config attribute** | `missing required config attribute`; `KeyError: 'effective_from_column'` | Diff the `{{ config(...) }}` block against the required key list | Add the missing config keys (`primary_key`, `effective_from_column`, etc.) to the model | [references/failure-modes/bitemporal-load-v2-misconfigured.md](references/failure-modes/bitemporal-load-v2-misconfigured.md) |
| 5 | **Warehouse not running** | `WAREHOUSE_NOT_RUNNING`; `HTTPError 404`; dbt query timeout | `databricks sql warehouses get <id>` — inspect `state` field | Start the warehouse via Databricks UI or Python SDK; set `auto_stop_mins > 0` | [references/failure-modes/warehouse-not-running.md](references/failure-modes/warehouse-not-running.md) |
| 6 | **Public PyPI 404 on dbt deps** | `Could not find a version...`; `pypi.org` or `files.pythonhosted.org` in URL | `grep -n "index-url\|cgrepo" dbt_wrapper.py requirements.txt` | Add `--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` to all pip calls | [references/failure-modes/public-pypi-404.md](references/failure-modes/public-pypi-404.md) |
| 7 | **Job task times out on cold start** | `Cluster startup time > 5 min`; `CLUSTER_REQUEST_LIMIT_EXCEEDED`; task timeout waiting for cluster | Check `databricks.yml` task spec for `job_cluster_key` vs `environment_key`; check `timeout_seconds` | Switch to serverless Python compute (`environment_key` + `client: "1"`) or raise `timeout_seconds` to ≥ 900 | [references/failure-modes/job-cold-start-timeout.md](references/failure-modes/job-cold-start-timeout.md) |

---

## General Diagnostic Workflow

1. **Identify the failure mode** — match the log output against symptom strings in the table above.
2. **Check the log level** — run `dbt --debug run ...` locally, or enable `log_level: DEBUG` in `dbt_project.yml` for cluster tasks.
3. **Isolate to local first** — reproduce with `dbt run --target local` before debugging bundle-run issues. Local failures are faster to iterate.
4. **Consult `/databricks-docs`** for official documentation on any Databricks API, configuration key, or error code encountered.
5. **Escalate** — if the issue is a missing CA bundle, blocked network endpoint, or cluster policy restriction, raise with the platform team rather than working around it.

---

## Related Skills

- `/run-dbt-on-databricks` — invocation guide for all three run modes.
- `/write-dbt-wrapper` — source for `dbt_wrapper.py` patterns including auth hydration, env-var injection, and pip index-url configuration.
- `/databricks-docs` — fetch official Databricks documentation on any topic (compute types, warehouses, secrets, SDK reference).
- `/databricks-bundles` — DAB manifest structure and deployment targets.
- `/databricks-jobs` — job YAML, cluster specs, timeout configuration.
- `/dbt-best-practices` — coding conventions and model structure guidance.
