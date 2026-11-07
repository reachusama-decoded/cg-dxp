# DBX-COMPUTE: Compute (Clusters and Warehouses)

Cluster and warehouse policy: pinning, Photon, auto-termination, init scripts.

## DBX-COMPUTE-001 — Job clusters for production; all-purpose for development only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + cluster-policy

**Decision.** Production scheduled work runs on job clusters. All-purpose
clusters are for interactive development only.

**Why.** All-purpose clusters cost-leak: they don't auto-terminate as
aggressively, they're shared, and they accumulate libraries from past
sessions.

## DBX-COMPUTE-002 — Pin Databricks Runtime version explicitly

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Cluster definitions pin a specific DBR version (e.g.,
`14.3.x-scala2.12`). Never `latest`, `auto`, or floating channels.

**Why.** DBR version determines Spark version, library versions, and
optimizer behavior. Floating versions break reproducibility silently.

## DBX-COMPUTE-003 — Photon enabled for SQL workloads

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Enable Photon (`runtime_engine: PHOTON`) on clusters
running SQL/Delta workloads.

**Why.** 2-3x typical speedup with no code changes. Cost vs. wall-clock
trade is favorable for almost all SQL.

**Exception.** Workloads using unsupported APIs (Photon supports a subset
of Spark APIs; check the docs for the runtime version).

## DBX-COMPUTE-004 — Auto-termination on all-purpose clusters within 30 minutes

**Severity:** error
**Since:** v0.1.0
**Linter:** cluster-policy

**Decision.** All-purpose clusters set `autotermination_minutes <= 30`.
Cluster policies enforce this.

**Why.** Cost control. An idle all-purpose cluster running for hours is
the highest-frequency cost incident at every Databricks shop.

## DBX-COMPUTE-005 — Cluster policies enforce instance types and budget caps

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform required

**Decision.** Cluster policies define allowed instance types, max worker
count, autoscaling bounds, and DBU budgets per workspace. All cluster
creation goes through a policy.

**Why.** Without policies, users provision oversized clusters by
accident. Policies are the only effective cost guardrail.

## DBX-COMPUTE-006 — Serverless SQL warehouses for BI; classic only when serverless cannot serve

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** BI workloads (dashboards, ad-hoc queries) use serverless
SQL warehouses. Use classic only when a feature gap blocks serverless.

**Why.** Serverless eliminates startup latency and right-sizes
automatically. Classic warehouses pay for idle.

## DBX-COMPUTE-007 — Init scripts in workspace files only, not DBFS

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Cluster init scripts live in workspace files (Git-backed)
or UC volumes. DBFS init scripts are deprecated and forbidden.

**Why.** DBFS init scripts can be modified outside version control and
have been deprecated by Databricks for security reasons.

### Workflows (Jobs and Orchestration)
