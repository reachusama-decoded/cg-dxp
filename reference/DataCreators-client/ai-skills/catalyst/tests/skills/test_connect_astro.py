"""Unit tests for the Astronomer connector (PY-SECURITY-*).

Mocks the `astro` CLI via subprocess.run. The skill directory uses a
hyphen (`connect-astro/`) which is not a valid Python module name, so
we load `astro_connect.py` via importlib.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ASTRO_CONNECT_PATH = (
    REPO_ROOT / "skills" / "connect-astro" / "scripts" / "astro_connect.py"
)


def _load_astro_connect():
    spec = importlib.util.spec_from_file_location(
        "connect_astro_astro_connect", ASTRO_CONNECT_PATH
    )
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def astro_connect():
    return _load_astro_connect()


def test_missing_token_exits_2(astro_connect, monkeypatch):
    monkeypatch.delenv("ASTRO_API_TOKEN", raising=False)
    with pytest.raises(SystemExit) as exc:
        astro_connect.main()
    assert exc.value.code == 2


def test_empty_token_exits_2(astro_connect, monkeypatch):
    monkeypatch.setenv("ASTRO_API_TOKEN", "")
    with pytest.raises(SystemExit) as exc:
        astro_connect.main()
    assert exc.value.code == 2


def _fake_run_factory(calls=None, login_returncode=0, login_stderr="", workspace_stdout=None):
    """Return a fake subprocess.run that records calls and fakes CLI output."""

    def fake_run(cmd, input_text=None, *args, **kwargs):
        if calls is not None:
            calls.append({"cmd": list(cmd), "input_text": input_text})
        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        if "login" in cmd:
            result.returncode = login_returncode
            result.stderr = login_stderr
            result.stdout = "Logged in.\n" if login_returncode == 0 else ""
        elif "context" in cmd and "list" in cmd:
            result.stdout = "NAME     DOMAIN\ndefault  astronomer.io\n"
        elif "workspace" in cmd and "list" in cmd:
            if workspace_stdout is not None:
                result.stdout = workspace_stdout
            else:
                result.stdout = (
                    "ID            NAME\n"
                    "ws-abc123     Catalyst Workspace\n"
                )
        elif "deployment" in cmd and "list" in cmd:
            result.stdout = (
                "ID            NAME\n"
                "dep-xyz789    catalyst-prod\n"
            )
        else:
            result.stdout = ""
        return result

    return fake_run


def test_happy_path_exit_0(astro_connect, monkeypatch, tmp_path):
    monkeypatch.setenv("ASTRO_API_TOKEN", "tok-secret-value")
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    monkeypatch.setattr(astro_connect, "_run", _fake_run_factory())

    # main() returns None on success (no SystemExit means exit 0)
    astro_connect.main()

    session_file = tmp_path / "astro_session.json"
    assert session_file.exists()
    data = json.loads(session_file.read_text())
    assert "workspace_id" in data
    assert data["workspace_id"] == "ws-abc123"
    assert "deployments" in data


def test_token_not_written_to_disk(astro_connect, monkeypatch, tmp_path):
    secret = "tok-this-must-never-land-on-disk"
    monkeypatch.setenv("ASTRO_API_TOKEN", secret)
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    monkeypatch.setattr(astro_connect, "_run", _fake_run_factory())

    astro_connect.main()

    # Scan every file under tmp_path for the secret.
    leaked = []
    for p in tmp_path.rglob("*"):
        if p.is_file():
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue
            if secret in content:
                leaked.append(str(p))
    assert leaked == [], f"token leaked to: {leaked}"


def test_token_never_in_argv(astro_connect, monkeypatch, tmp_path):
    secret = "tok-argv-must-be-clean"
    monkeypatch.setenv("ASTRO_API_TOKEN", secret)
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    calls = []
    monkeypatch.setattr(astro_connect, "_run", _fake_run_factory(calls=calls))

    astro_connect.main()

    assert calls, "expected the fake runner to record at least one call"
    for call in calls:
        for arg in call["cmd"]:
            assert secret not in arg, f"token leaked to argv: {call['cmd']}"


def test_token_delivered_via_stdin(astro_connect, monkeypatch, tmp_path):
    secret = "tok-stdin-delivery"
    monkeypatch.setenv("ASTRO_API_TOKEN", secret)
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    calls = []
    monkeypatch.setattr(astro_connect, "_run", _fake_run_factory(calls=calls))

    astro_connect.main()

    login_calls = [c for c in calls if "login" in c["cmd"]]
    assert len(login_calls) == 1
    assert login_calls[0]["input_text"] == secret


def test_login_failure_exits_3(astro_connect, monkeypatch, tmp_path):
    monkeypatch.setenv("ASTRO_API_TOKEN", "tok")
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    monkeypatch.setattr(
        astro_connect,
        "_run",
        _fake_run_factory(login_returncode=1, login_stderr="bad token"),
    )

    with pytest.raises(SystemExit) as exc:
        astro_connect.main()
    assert exc.value.code == 3


def test_empty_workspace_list_exits_4(astro_connect, monkeypatch, tmp_path):
    monkeypatch.setenv("ASTRO_API_TOKEN", "tok")
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    # Only the header row, no data rows.
    monkeypatch.setattr(
        astro_connect,
        "_run",
        _fake_run_factory(workspace_stdout="ID            NAME\n"),
    )

    with pytest.raises(SystemExit) as exc:
        astro_connect.main()
    assert exc.value.code == 4


def test_token_redacted_in_stderr(astro_connect, monkeypatch, tmp_path, capsys):
    secret = "tok-redact-me-from-stderr"
    monkeypatch.setenv("ASTRO_API_TOKEN", secret)
    monkeypatch.setenv("ASTRO_SESSION_DIR", str(tmp_path))
    monkeypatch.setattr(
        astro_connect,
        "_run",
        _fake_run_factory(
            login_returncode=1,
            login_stderr=f"auth failed with token={secret}",
        ),
    )

    with pytest.raises(SystemExit):
        astro_connect.main()

    err = capsys.readouterr().err
    assert secret not in err
    assert "***" in err
