from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
pytestmark = pytest.mark.devcontainer


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_json_permissive(text: str) -> dict:
    """Load JSON that may contain // line comments or /* */ block comments."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r",\s*([\]\}])", r"\1", text)
    return json.loads(text)

def test_devcontainer_uses_dind_run_args() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    run_args = cfg.get("runArgs", [])
    mounts = cfg.get("mounts", [])
    # Require explicit dind flags and no docker socket mount when using dind wiring.
    has_flags = "--privileged" in run_args and "--init" in run_args
    no_sock_mount = not any("/var/run/docker.sock" in m for m in mounts)
    assert has_flags, "devcontainer runArgs must include --privileged and --init"
    assert no_sock_mount, "devcontainer must not mount /var/run/docker.sock when using dind wiring"


def test_post_start_command_uses_repo_script() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    post = cfg.get("postStartCommand", "")
    # Require the repo's post-start script to be used for postStartCommand
    assert "post-start.sh" in post, "postStartCommand must include post-start.sh"


def test_post_start_heals_dockerd_before_health_check() -> None:
    script = _read(".devcontainer/post-start.sh")
    assert "/usr/local/bin/start-dockerd.sh" in script
    assert "/usr/local/bin/ensure-dockerd.sh" in script
    assert "/usr/local/bin/dpc-check" in script


def test_fresh_clone_does_not_require_an_untracked_env_file_to_start() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    run_args = cfg.get("runArgs", [])
    assert "--env-file" not in run_args

    mise = _read(".mise.toml")
    assert "cp .devcontainer/utils/.env.example .devcontainer/.env" in mise
    assert '_.file = ".devcontainer/.env"' not in mise


def test_dockerd_lifecycle_serializes_start_and_heals_async() -> None:
    start = _read(".devcontainer/start-dockerd.sh")
    ensure = _read(".devcontainer/ensure-dockerd.sh")

    assert "dockerd-start.lock" in start
    assert "mkdir \"$lock_dir\"" in start
    assert "ps -ef | awk '$0 ~ /[ /](dockerd|containerd)([ ]|$)/ {print $2}'" not in start
    assert "grep -E '[ /](dockerd|containerd)([ ]|$)'" in start
    assert "--no-wait" in start
    assert "nohup /usr/local/bin/start-dockerd.sh --restart --no-wait" in ensure
    assert "DPC_SKIP_DOCKERD_HEAL" in ensure
    assert "pgrep -x dockerd" in ensure
    assert "for pid in" not in ensure


def test_interactive_shell_triggers_dockerd_heal() -> None:
    bashrc = _read(".devcontainer/utils/bashrc")
    assert "/usr/local/bin/ensure-dockerd.sh" in bashrc


def test_post_start_sanitizes_devcontainer_docker_credstore() -> None:
    post_start = _read(".devcontainer/post-start.sh")
    assert "credsStore" in post_start
    assert "dev-containers-" in post_start
    assert "jq 'del(.credsStore)'" in post_start


def test_devcontainer_forwards_oauth_and_airflow_ports() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    ports = cfg.get("forwardPorts", [])
    assert 8020 in ports
    assert 8080 in ports
    assert 6563 in ports


def test_troubleshooting_uses_inner_docker_daemon() -> None:
    guide = _read(".devcontainer/TROUBLESHOOTING.md")
    assert "/var/run/docker.sock" not in guide
    assert "/usr/local/bin/ensure-dockerd.sh" in guide
