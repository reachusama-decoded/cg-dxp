"""Astronomer CLI connector (PY-SECURITY-*).

Authenticates to Astronomer using an API token from the env var
`ASTRO_API_TOKEN` (sourced from the platform secrets backend). The
token is piped to `astro login --token-stdin` and is never written
to argv or disk. Non-secret session metadata is recorded to
`${ASTRO_SESSION_DIR}/astro_session.json` (a tmpdir by default).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


_TOKEN: str | None = None


def fail(code: int, message: str) -> None:
    if _TOKEN:
        message = message.replace(_TOKEN, "***")
    print(message, file=sys.stderr)
    sys.exit(code)


def _run(cmd, input_text: str | None = None):
    """Thin wrapper around subprocess.run so tests can monkeypatch it."""
    return subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_table_first_row(stdout: str) -> dict[str, str]:
    """Parse a 2-line `astro` CLI table (header + first data row) into a dict."""
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if len(lines) < 2:
        return {}
    headers = lines[0].split()
    values = lines[1].split(None, len(headers) - 1)
    return dict(zip(headers, values))


def _parse_table_rows(stdout: str) -> list[dict[str, str]]:
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if len(lines) < 2:
        return []
    headers = lines[0].split()
    rows = []
    for ln in lines[1:]:
        values = ln.split(None, len(headers) - 1)
        rows.append(dict(zip(headers, values)))
    return rows


def main() -> None:
    global _TOKEN
    token = os.environ.get("ASTRO_API_TOKEN")
    if not token:
        fail(
            2,
            "ASTRO_API_TOKEN is unset or empty. Source the token from the "
            "platform secrets backend (PY-SECURITY-*). Plaintext-token "
            "persistence is forbidden.",
        )
    _TOKEN = token

    login = _run(["astro", "login", "--token-stdin"], input_text=token)
    if login.returncode != 0:
        fail(3, f"astro login failed: {login.stderr.strip()}")

    context = _run(["astro", "context", "list"])
    if context.returncode != 0:
        fail(3, f"astro context list failed: {context.stderr.strip()}")
    context_row = _parse_table_first_row(context.stdout)

    workspaces = _run(["astro", "workspace", "list"])
    if workspaces.returncode != 0:
        fail(3, f"astro workspace list failed: {workspaces.stderr.strip()}")
    workspace_rows = _parse_table_rows(workspaces.stdout)
    if not workspace_rows:
        fail(4, "No Astronomer workspaces available for this token.")
    workspace = workspace_rows[0]

    deployments = _run(["astro", "deployment", "list"])
    deployment_rows = (
        _parse_table_rows(deployments.stdout) if deployments.returncode == 0 else []
    )

    session_dir = Path(os.environ.get("ASTRO_SESSION_DIR") or tempfile.mkdtemp(prefix="astro-session-"))
    session_dir.mkdir(parents=True, exist_ok=True)
    session_path = session_dir / "astro_session.json"

    workspace_id = workspace.get("ID") or next(iter(workspace.values()), "")
    workspace_name = workspace.get("NAME", "")

    metadata = {
        "context": context_row,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "deployments": [
            {
                "id": d.get("ID", ""),
                "name": d.get("NAME", ""),
            }
            for d in deployment_rows
        ],
        "auth_type": "astro-api-token",
    }
    session_path.write_text(json.dumps(metadata, indent=2))

    print(f"Connected to Astronomer workspace {workspace_id} ({workspace_name}).")
    print(f"Deployments: {len(deployment_rows)}")
    print(f"Session metadata: {session_path}")


if __name__ == "__main__":
    main()
