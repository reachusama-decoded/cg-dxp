# CONT-PATH: Paths and Interpreter

Workspace, virtual environment, and interpreter paths. The dominant cause of a
broken vended container is a path keyed to a user, home directory, host, or
literal repo name.

## CONT-PATH-001 — No host- or home-relative hardcoded paths

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Container configuration (`Dockerfile`, Compose files,
`devcontainer.json`, setup scripts, task-runner config) must not hardcode a host
absolute path, a `/home/<user>/` path, or any path that assumes a specific
developer machine. Interpreter and virtual-environment paths resolve to a
location that exists inside the container regardless of who built it.

**Why.** A path like `/home/vscode/.venv` is a stale template default that does
not match where the environment is actually created. When the interpreter
points at a non-existent path, the container builds but every Python tool,
language server, and task fails. Host absolute paths break the moment another
developer (or CI) opens the repo.

**Exception.** None.

**Examples.**
```jsonc
// ✗ — interpreter hardcoded to a home-relative venv that is never created there
"python.defaultInterpreterPath": "/home/vscode/.venv/bin/python"

// ✓ — interpreter points at the workspace venv that setup actually creates
"python.defaultInterpreterPath": "/workspace/.venv/bin/python"
```

## CONT-PATH-002 — Single source of truth for the virtual-environment path

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Define the virtual-environment path in exactly one place — the
task-runner config (`_.python.venv` for mise, the equivalent for poe/uv) — and
have every other consumer reference that same location. `UV_PROJECT_ENVIRONMENT`,
`python.defaultInterpreterPath`, and `terminal.integrated.env.*` must all resolve
to the same path.

**Why.** When the venv path is declared independently in three files, they drift.
The interpreter ends up pointing somewhere the venv was never created. One
declaration keeps creation, activation, and the editor in agreement.

**Exception.** None.

**Examples.**
```toml
# .mise.toml — the single declaration
[env]
_.python.venv = { path = "/workspace/.venv", create = true }
UV_PROJECT_ENVIRONMENT = "/workspace/.venv"
```
```jsonc
// editor/container metadata references the same path, never a new one
"python.defaultInterpreterPath": "/workspace/.venv/bin/python"
```

## CONT-PATH-003 — Derive the workspace location from the container, not a literal repo name

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + shellcheck

**Decision.** Scripts that need the workspace directory derive it from the
container — `WORKSPACE_BASENAME` (set from `${localWorkspaceFolderBasename}` in
`remoteEnv`) or a fixed mount target such as `/workspace`. Never hardcode
`/workspaces/<specific-repo-name>`.

**Why.** A script that does `cd /workspaces/edo-ig-data-products` only works in
the one repo it was written for. The same script vended into another repo
silently operates on the wrong (or missing) directory. Deriving the path keeps
the script repo-agnostic and re-vendable.

**Exception.** None.

**Examples.**
```sh
# ✗ — only works in one repo
cd /workspaces/edo-ig-data-products

# ✓ — repo-agnostic, works wherever it is vended
if [ -n "${WORKSPACE_BASENAME:-}" ] && [ -d "/workspaces/${WORKSPACE_BASENAME}" ]; then
    cd "/workspaces/${WORKSPACE_BASENAME}"
fi
```
