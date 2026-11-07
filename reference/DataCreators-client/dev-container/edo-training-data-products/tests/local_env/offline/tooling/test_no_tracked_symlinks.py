"""Guard: no tracked file may be a git symlink.

Why: Git for Windows clones with core.symlinks=false by default (it needs Developer
Mode or admin rights to create real symlinks). A tracked symlink then checks out as a
plain text file whose *contents* are the link target path. Anything that reads the file
gets the path string instead of the real payload.

This bit us concretely: challenges/v1/02-dbt-pipeline/dbt/profiles.yml and
data_products/atlas_elt/profiles.yml were committed as symlinks so that raw `dbt`
commands could resolve a profile from the project dir. On Windows they checked out as
28-byte text files, and the first command of Challenge 02 (`dbt debug`) died with an
unreadable traceback: AttributeError: 'str' object has no attribute 'get'.

Use a real file copy plus a content-equality test instead (see
tests/challenges/offline/test_ch02.py and test_ch04_structure.py).
"""

from __future__ import annotations

import subprocess

from tests.challenges.conftest import repo_root

GIT_SYMLINK_MODE = "120000"


def test_no_tracked_symlinks() -> None:
    out = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    symlinks = [
        line.split("\t", 1)[1]
        for line in out.splitlines()
        if line.startswith(GIT_SYMLINK_MODE + " ")
    ]

    assert not symlinks, (
        "Tracked symlinks break Windows clones (core.symlinks=false checks them out as "
        "text files containing the target path). Commit a real file instead:\n  "
        + "\n  ".join(symlinks)
    )
