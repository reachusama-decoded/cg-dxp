"""Guard: every tracked dbt profile must disable the pandas result conversion.

Why: dbt-databricks converts query result sets through pandas by default. On this
image (Python 3.13 + databricks-sql-connector + pyarrow) that conversion segfaults the
CPython interpreter on the first query that returns rows. The process dies with exit
139 and *no error message* -- often no output at all when the parse cache is warm, so
`dbt seed` appears to succeed with exit 0 while having done nothing.

`connection_parameters: {_disable_pandas: true}` avoids that code path entirely.

This bit us concretely: data_products/atlas_elt was the only profile in the repo
missing it, which made all of Challenge 04 unrunnable -- `dbt debug` passed (the
handshake returns no rows) and then every seed/run/build/test/compile/show segfaulted.
"""

from __future__ import annotations

import subprocess

import yaml

from tests.challenges.conftest import repo_root


def _tracked_profiles() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*profiles.yml"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def test_every_databricks_profile_disables_pandas() -> None:
    profiles = _tracked_profiles()
    assert profiles, "expected to find tracked profiles.yml files"

    offenders: list[str] = []
    for rel in profiles:
        data = yaml.safe_load((repo_root() / rel).read_text())
        if not isinstance(data, dict):
            continue
        for profile_name, profile in data.items():
            if not isinstance(profile, dict):
                continue
            for target_name, target in (profile.get("outputs") or {}).items():
                if not isinstance(target, dict) or target.get("type") != "databricks":
                    continue
                params = target.get("connection_parameters") or {}
                if params.get("_disable_pandas") is not True:
                    offenders.append(f"{rel}::{profile_name}.outputs.{target_name}")

    assert not offenders, (
        "These databricks targets are missing "
        "`connection_parameters: {_disable_pandas: true}`. Without it, dbt segfaults "
        "(exit 139, no error) on the first query returning rows:\n  "
        + "\n  ".join(offenders)
    )
