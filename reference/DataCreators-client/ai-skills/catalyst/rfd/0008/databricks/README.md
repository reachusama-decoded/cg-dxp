# Databricks and Unity Catalog Standards

## Governing Authority

These standards are derived from and comply with:

- [Databricks Documentation](https://docs.databricks.com/)
- [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [Databricks Workflows Documentation](https://docs.databricks.com/en/workflows/index.html)
- [Databricks Security and Compliance](https://www.databricks.com/trust/security-features)
- [Databricks Cluster Policies](https://docs.databricks.com/en/admin/clusters/policies.html)

These rules apply to platform-config concerns that aren't tied to a specific
language — Delta Lake operations, Unity Catalog governance, cluster and
warehouse policy, workflow patterns, and Databricks-specific security. Rules
that surface in SQL files (partition pruning, `merge` strategy, Z-ORDER) live
in `sql.md`.

## Rule Format

Same shape as the rest of RFD 0008:

```
### DBX-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** advisory / Terraform validate / cluster-policy / etc.

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** good / bad config.
```

Categories: `DELTA`, `UC`, `COMPUTE`, `WORKFLOW`, `SEC`.

## Current Platform Posture

Two decisions worth surfacing up front because they shape several rules below:

1. **External tables preferred over managed.** Catalyst data products
   currently land in cloud storage (S3 / ADLS) governed by external locations
   in UC. Managed tables move data into Databricks-managed storage and are
   not the default today. Migration to managed-by-default is gated on a
   separate decision (storage cost analysis + cross-tool query parity). See
   `DBX-UC-003`.
2. **OAuth client credentials for service-principal auth, never PAT.**
   Personal Access Tokens are forbidden for Model Serving and any
   service-to-service Databricks call. See `DBX-SEC-002`.

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`compute.md`](compute.md) — **Compute (Clusters and Warehouses)** (7 rules). Cluster and warehouse policy: pinning, Photon, auto-termination, init scripts.
- [`delta.md`](delta.md) — **Delta Lake** (9 rules). Delta Lake operations: format, clustering, vacuum, schema evolution, time travel.
- [`sec.md`](sec.md) — **Security** (5 rules). Secrets, OAuth client credentials, PrivateLink, IP allowlists, audit logs.
- [`uc.md`](uc.md) — **Unity Catalog** (10 rules). Unity Catalog governance: three-part names, ownership, tags, IaC for grants.
- [`workflow.md`](workflow.md) — **Workflows (Jobs and Orchestration)** (6 rules). Databricks Workflows: timeouts, retries, notifications, declarative DAGs.
