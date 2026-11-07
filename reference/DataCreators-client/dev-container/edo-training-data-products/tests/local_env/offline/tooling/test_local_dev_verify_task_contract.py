import os
import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_mise_has_local_dev_verify_task() -> None:
    mise = tomllib.loads(_read(".mise.toml"))
    task = mise["tasks"]["verify:local-dev"]
    run = task["run"]
    assert "dpc-check" in run
    assert "pytest tests/local_env/offline" in run
    assert "verify-with-databricks.sh" in run


def test_verify_local_dev_task_runs_in_command_order(tmp_path) -> None:
    run = tomllib.loads(_read(".mise.toml"))["tasks"]["verify:local-dev"]["run"]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "calls.log"

    stubs = {
        "dpc-check": "#!/bin/sh\necho dpc-check >>\"$LOG_FILE\"\n",
        "pytest": "#!/bin/sh\necho pytest \"$@\" >>\"$LOG_FILE\"\n",
        "bash": "#!/bin/sh\necho bash \"$@\" >>\"$LOG_FILE\"\nexit 0\n",
    }
    for name, body in stubs.items():
        path = bin_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    env["LOG_FILE"] = str(log_file)
    env["CERT_INTEGRATION_TESTS"] = "0"

    result = subprocess.run(
        ["/bin/bash", "-c", run],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert log_file.read_text(encoding="utf-8").splitlines() == [
        "dpc-check",
        "pytest tests/local_env/offline",
        "bash scripts/verify-with-databricks.sh",
    ]


def test_docs_reference_new_local_env_pytest_paths() -> None:
    docs = [_read("README.md"), _read("GETTING_STARTED.md"), _read(".devcontainer/README.md")]
    joined = "\n".join(docs)
    assert "tests/local_env/offline" in joined
    assert "tests/local_env/live" in joined
