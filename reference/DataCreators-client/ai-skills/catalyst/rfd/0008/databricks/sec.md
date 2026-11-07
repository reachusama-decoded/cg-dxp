# DBX-SEC: Security

Secrets, OAuth client credentials, PrivateLink, IP allowlists, audit logs.

## DBX-SEC-001 — Secrets in Databricks secret scopes only

**Severity:** error
**Since:** v0.1.0
**Linter:** gitleaks + advisory

**Decision.** All secrets (tokens, passwords, API keys, connection
strings) live in Databricks secret scopes. Never inline in notebooks,
init scripts, or job parameters.

**Why.** Secret scopes are auditable and access-controlled. Inline
secrets leak via job logs, notebook exports, and history APIs.

**Exception.** None.

## DBX-SEC-002 — OAuth client credentials for service-principal auth; never PAT

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + audit

**Decision.** Service-to-service authentication uses OAuth 2.0 client
credentials (CLIENT_ID + CLIENT_SECRET) for service principals. Personal
Access Tokens are forbidden for Model Serving and any non-interactive
Databricks call.

**Why.** PATs are tied to individual users — they break when the user
leaves, can't be rotated centrally, and grant the user's full
permissions. OAuth client credentials are scoped to a service principal,
rotated independently, and integrate with CG SSO.

**Examples.**
```python
# ✓
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(
    host=host,
    client_id=os.environ["DATABRICKS_CLIENT_ID"],
    client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
)

# ✗ — PAT for service-to-service
w = WorkspaceClient(host=host, token=os.environ["DATABRICKS_PAT"])
```

## DBX-SEC-003 — PrivateLink for production catalog access

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Production workspaces accessing production catalogs route
over AWS PrivateLink / Azure Private Link. Public-internet endpoints to
production catalogs are forbidden.

**Why.** Reduces attack surface and meets CG network-security
requirements for regulated workloads.

## DBX-SEC-004 — IP allowlists configured per workspace

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Each workspace has an IP-allowlist policy in Terraform. The
default-deny applies; CG corporate ranges and approved CI runners are
explicitly listed.

**Why.** Defense in depth. Even with PrivateLink, IP allowlisting blocks
exfiltration via stolen credentials from unexpected networks.

## DBX-SEC-005 — Audit log delivery enabled

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Workspace audit log delivery is configured to an S3 bucket
or log aggregator. Retention follows CG audit policy (typically 7 years).

**Why.** UC audit data alone is not sufficient — workspace-level events
(cluster events, job runs, notebook commands) are only in the workspace
audit log.
