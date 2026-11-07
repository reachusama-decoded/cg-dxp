"""Guard: challenge 03's stubs/ must match the live portfolio_analytics product.

Why: `mise run challenge:reset 03` does a blanket `cp -R challenges/v1/03-airflow-orchestration/
stubs/. data_products/portfolio_analytics/`. That copies *everything* in stubs/, not just the
files a trainee authors. So any file that drifts between the two trees gets silently overwritten
in the live product the moment someone runs reset.

This bit us concretely: `check-dag-load.sh` had been improved in the live product (it grew DagBag
structural probes) but the stubs/ and solution/ copies were left on the older version. Running the
documented `mise run challenge:reset 03` downgraded the live tooling script and left a confusing
unexplained diff in `git status`.

The invariant is checked against the **git index** (staged content), not the working tree, so a
trainee with the challenge half-finished does not trip it. For an unmodified file the index matches
HEAD, so this is equivalent to checking the committed state in CI.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.challenges.conftest import repo_root

STUBS = "challenges/v1/03-airflow-orchestration/stubs"
LIVE = "data_products/portfolio_analytics"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _blob(path: str) -> str | None:
    # This project is also distributed inside the course repository. Index blob
    # names are relative to the Git root, unlike ls-files output from this cwd.
    prefix = _git("rev-parse", "--show-prefix").strip()
    proc = subprocess.run(
        ["git", "show", f":{prefix}{path}"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
    )
    return proc.stdout if proc.returncode == 0 else None


def test_ch03_stubs_match_the_live_product() -> None:
    inside = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root(), capture_output=True, text=True
    )
    if inside.returncode != 0:
        pytest.skip("not in a Git work tree (e.g. the authoring container's CLIENT_ROOT or a learner package)")
    tracked = [p for p in _git("ls-files", f"{STUBS}/").splitlines() if p.strip()]
    assert tracked, "expected tracked files under challenge 03 stubs/"

    mismatched: list[str] = []
    for stub_path in tracked:
        rel = stub_path[len(STUBS) + 1 :]
        live_path = f"{LIVE}/{rel}"
        stub_blob = _blob(stub_path)
        live_blob = _blob(live_path)
        if live_blob is None:
            mismatched.append(f"{rel} (no counterpart at {live_path})")
        elif stub_blob != live_blob:
            mismatched.append(rel)

    assert not mismatched, (
        "challenge:reset 03 copies all of stubs/ over data_products/portfolio_analytics/, so "
        "these drifted files would be silently overwritten in the live product:\n  "
        + "\n  ".join(mismatched)
    )
