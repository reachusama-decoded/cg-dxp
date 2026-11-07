from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
REFRESHER = ".devcontainer/utils/databricks-oauth-refresh.sh"



def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


import os as _os_refresher
import subprocess as _sp_refresher


def test_oauth_refresher_forces_refresh_on_scheduler_reappearance() -> None:
    script = _read(".devcontainer/utils/databricks-oauth-refresh.sh")
    assert "last_scheduler" in script
    assert "scheduler_changed" in script
    # The refresher must inspect container identity (ID) so recreation is detected
    assert "docker ps --format '{{.ID}} {{.Names}}'" in script or "docker ps --format '{{.ID}}'" in script
    assert "sleep_s=1" in script or "sleep_s=0" in script


def test_oauth_refresher_checks_scheduler_while_waiting() -> None:
    script = _read(".devcontainer/utils/databricks-oauth-refresh.sh")
    # Long sleeps should be chunked so the refresher can detect scheduler changes while waiting.
    assert "remaining=$sleep_s" in script
    assert 'while [ "$remaining" -gt 0 ]' in script
    assert 'sleep "$chunk"' in script
    assert "resolve_scheduler" in script
    assert "breaking early to refresh" in script or "scheduler identity changed during wait" in script


def test_oauth_refresher_reports_retryable_failure_when_connection_upsert_fails(tmp_path) -> None:
    home = tmp_path / "home"
    config_dir = home / ".config" / "dpc"
    config_dir.mkdir(parents=True)
    (config_dir / "databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )

    import os
    import subprocess

    result = subprocess.run(
        [
            "bash",
            "-c",
            f'''
source "{(REPO_ROOT / REFRESHER).as_posix()}" --source-only
resolve_scheduler() {{ printf '%s\\n' fake-scheduler; }}
mint_payload() {{
  printf '%s\\n' '{{"access_token":"token","expiry":"2030-01-01T00:00:00Z"}}'
}}
upsert_connection() {{
  if [ "$2" = "databricks_default" ]; then
    return 1
  fi
  return 0
}}
refresh_once
printf 'rc=%s\\n' "$?"
''',
        ],
        cwd=home,
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "rc=2" in result.stdout
    status = json.loads((config_dir / "oauth-refresh-status.json").read_text(encoding="utf-8"))
    assert status["state"] == "connection_update_failed"
    assert status["token_expiry"] == ""


def test_validate_pat_token_has_no_unreachable_duplicate_block() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    # The Me-probe curl must appear exactly once inside validate_pat_token.
    assert script.count('/api/2.0/preview/scim/v2/Me') == 1
    # No code after the function's successful 'return 0' before the closing brace.
    func = script.split("validate_pat_token() {", 1)[1].split("\n}", 1)[0]
    lines_after_return = func.split("return 0", 1)[1].strip()
    assert lines_after_return == "", (
        "validate_pat_token has unreachable code after 'return 0':\n" + lines_after_return
    )


def test_oauth_refresher_exists_and_is_executable() -> None:
    path = REPO_ROOT / REFRESHER
    assert path.exists(), "refresher script missing"
    assert _os_refresher.access(path, _os_refresher.X_OK), "refresher script must be executable"


def test_oauth_refresher_core_contract() -> None:
    script = _read(REFRESHER)
    # Mode gate: no-op unless oauth.
    assert 'if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then' in script
    # Browser-free minting only.
    assert "databricks auth token" in script
    assert "databricks auth login" not in script
    # Scheduler discovery by dynamic-hash pattern.
    assert "^edo-training.*-scheduler-1$" in script
    # Upserts BOTH connection ids via the Airflow CLI.
    assert "databricks_default" in script
    assert "caspian-training-databricks" in script
    assert "airflow connections add" in script
    assert "airflow connections delete" in script
    # Heartbeat + log destinations from the design.
    assert "oauth-refresh-status.json" in script
    assert "/var/log/dbx-oauth-refresh.log" in script
    # Bearer connection shape: empty login (NOT login: token).
    assert '"login": ""' in script
    assert '"login": "token"' not in script


def test_oauth_refresher_is_noop_when_mode_is_pat(tmp_path) -> None:
    home = tmp_path
    cfg_dir = home / ".config" / "dpc"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "databricks.env").write_text("export DPC_DATABRICKS_AUTH_MODE=pat\n")
    # Normal PATH so bash/coreutils resolve; the no-op guarantee comes from the
    # mode gate returning before any docker/databricks call, not PATH starvation.
    env = {"HOME": str(home), "PATH": _os_refresher.environ.get("PATH", "")}
    result = _sp_refresher.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--once"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_oauth_refresher_loop_contract() -> None:
    script = _read(REFRESHER)
    assert "--loop" in script
    assert "DPC_SKIP_OAUTH_REFRESH" in script
    assert "oauth-refresh.pid" in script
    assert "kill -0" in script
    assert "seconds_until_refresh" in script
    assert "3300" in script
    assert "120" in script


def test_oauth_refresher_loop_opts_out_immediately(tmp_path) -> None:
    home = tmp_path
    (home / ".config" / "dpc").mkdir(parents=True)
    (home / ".config" / "dpc" / "databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
    )
    env = {
        "HOME": str(home),
        "PATH": _os_refresher.environ.get("PATH", ""),
        "DPC_SKIP_OAUTH_REFRESH": "1",
    }
    result = _sp_refresher.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--loop"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_seconds_until_refresh_helper(tmp_path) -> None:
    probe = (
        f'source "{REPO_ROOT / REFRESHER}" --source-only 2>/dev/null; '
        'seconds_until_refresh ""; '
        'echo "---"; '
        'seconds_until_refresh "not-a-date"'
    )
    result = _sp_refresher.run(
        ["bash", "-c", probe],
        env={"HOME": str(tmp_path), "PATH": _os_refresher.environ.get("PATH", "")},
        capture_output=True, text=True, timeout=30,
    )
    out = [line for line in result.stdout.splitlines() if line.strip()]
    assert out[0] == "3300"
    assert out[-1] == "3300"


def test_mise_has_oauth_refresh_task() -> None:
    toml = _read(".mise.toml")
    assert '[tasks."databricks:oauth-refresh"]' in toml
    assert "databricks-oauth-refresh.sh" in toml


def test_dpc_check_reports_auth_mode_and_refresher_health() -> None:
    script = _read(".devcontainer/check.sh")
    assert "DPC_DATABRICKS_AUTH_MODE" in script
    assert "oauth-refresh-status.json" in script
    assert "setup:databricks" in script or "setup-databricks-dbt.sh" in script
    assert "--pat" in script


def test_dpc_check_refresher_health_is_read_only() -> None:
    script = _read(".devcontainer/check.sh")
    region = script.split("oauth-refresh-status.json", 1)[1][:400]
    assert "databricks " not in region, "heartbeat check must be read-only (no CLI call)"


def test_readme_documents_single_mode_auth_and_refresher() -> None:
    readme = _read(".devcontainer/README.md")
    assert "DPC_DATABRICKS_AUTH_MODE" in readme
    assert "OAuth" in readme and "PAT" in readme
    assert "databricks-oauth-refresh.sh" in readme or "token refresher" in readme
    assert "setup:databricks" in readme or "setup-databricks-dbt.sh" in readme
