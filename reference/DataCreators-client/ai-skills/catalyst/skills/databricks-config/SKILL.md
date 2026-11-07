---
name: databricks-config
description: |
  Manage Databricks workspace connections: check current workspace, switch profiles, list available
  workspaces, or authenticate to a new workspace. Use when the user mentions "switch workspace",
  "which workspace", "current profile", "databrickscfg", "connect to workspace", or "databricks auth".
  Catalyst trigger phrases: "Databricks auth setup", "configure databricks profile", "set up workspace config".
allowed-tools: Read Bash Write Edit
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-SEC-001
    - DBX-SEC-002
  upstream-source: databricks-solutions/ai-dev-kit/databricks-skills/databricks-config
  upstream-commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
  upstream-license: Databricks (custom — see third-party/LICENSE-databricks.md)
  catalyst-modifications: |
    Modified by Capital Group on 2026-05-14:
    - dropped MCP tool references entirely (Catalyst policy); replaced with CLI + Python SDK + databricks_tools_core guidance
    - added metadata.standards citations (RFD 0008)
    - added Catalyst trigger phrases in description
---

> _Modified from `databricks-solutions/ai-dev-kit/databricks-skills/databricks-config` by Capital Group on 2026-05-14. See `metadata.catalyst-modifications` for the change set._

# Databricks Workspace Configuration

Manage Databricks workspace connections, profile switching, and authentication via the Databricks CLI and Python SDK.

## Steps

1. Determine the user's intent:
   - **status / which workspace / current** → show active profile, host, and username
   - **list / available workspaces** → list all profiles in `~/.databrickscfg`
   - **switch to X** → list profiles first, then switch active profile
   - **login / connect / authenticate** → run interactive login for a new workspace

2. Map intent to the appropriate action below.

3. Present the result. For status/switch/login: show host, profile, username. For list: formatted table with the active profile marked.

---

## Actions

### Status — Check Current Workspace

```bash
databricks auth env
```

Or via the Python SDK:

```python
from skills.clients.databricks_tools_core.auth import get_active_workspace

info = get_active_workspace()
print(f"Host: {info['host']}\nProfile: {info['profile']}\nUser: {info['user']}")
```

### List — Available Profiles

```bash
databricks auth profiles
```

This reads `~/.databrickscfg` and lists all configured profiles with their host URLs.

### Switch — Change Active Profile

```bash
# Set environment variable for the current session
export DATABRICKS_CONFIG_PROFILE=<profile-name>

# Or pass profile inline
databricks auth env --profile <profile-name>
```

> **Note:** The session-scoped environment variable resets on shell restart. For a permanent default, update `~/.databrickscfg` and set `[DEFAULT]` to the desired profile, or configure `cluster_id` or `serverless_compute_id = auto` in the profile block.

### Login — Authenticate to a New Workspace

```bash
# Interactive OAuth login (recommended)
databricks auth login --host https://<workspace-host> --profile <profile-name>

# After login, verify the connection
databricks auth env --profile <profile-name>
```

The login flow opens a browser window for OAuth. For service principal or PAT-based auth:

```bash
# PAT (Personal Access Token) — add to ~/.databrickscfg manually
# [my-profile]
# host = https://<workspace-host>
# token = dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## Python SDK — Workspace Operations

To perform workspace operations programmatically, invoke the corresponding function in `skills/clients/databricks_tools_core/`:

```python
from databricks.sdk import WorkspaceClient

# Default profile (from DATABRICKS_CONFIG_PROFILE or ~/.databrickscfg [DEFAULT])
w = WorkspaceClient()

# Explicit profile
w = WorkspaceClient(profile="my-profile")

# Explicit host + token
w = WorkspaceClient(host="https://<workspace>", token="<token>")

# Check current user
me = w.current_user.me()
print(f"User: {me.user_name}")
print(f"Host: {w.config.host}")
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `DATABRICKS_HOST not set` | Run `databricks auth login` or set `DATABRICKS_CONFIG_PROFILE` |
| `403 Forbidden` | Token expired or insufficient permissions; re-run `databricks auth login` |
| Wrong workspace active | `export DATABRICKS_CONFIG_PROFILE=<correct-profile>` |
| Profile not in list | Add `[profile-name]` block to `~/.databrickscfg` with `host` and `token` or OAuth config |
| PAT expired | Generate a new token from the workspace UI under User Settings > Access Tokens |

---

## Security Notes (DBX-SEC-001, DBX-SEC-002)

- Prefer OAuth (`databricks auth login`) over PATs for interactive sessions.
- Store PATs in `~/.databrickscfg` (file permissions `600`), never in source code or CI environment variable plain text.
- For CI/CD, use a service principal with OAuth M2M; inject credentials via secrets management (e.g., Harness secrets, Vault).
- Rotate PATs on a schedule; set expiry when creating tokens.
