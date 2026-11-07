"""CI guard: no references to legacy skill names outside the allowlist.

Legacy skills generate-dbt-model, validate-sql are being removed in
PR 2a (superseded by the new verb-noun skills). This test fails if any
file in the tree references them unless the file path is on the
allowlist (historical plans, this test, etc.).

Note: generate-dag is intentionally NOT in this list. RBAP's PR #98
landed it as the canonical Airflow-authoring skill; it stays.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Iterator

import yaml

LEGACY = ("generate-dbt-model", "validate-sql")
REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_FILE = REPO_ROOT / "scripts" / "ci" / "legacy-skill-allowlist.txt"


def _allowlist() -> set[str]:
    if not ALLOWLIST_FILE.exists():
        return set()
    return {
        line.strip()
        for line in ALLOWLIST_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def _tracked_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    )
    return [REPO_ROOT / line for line in out.splitlines() if line]


def test_no_legacy_skill_references_outside_allowlist():
    allow = _allowlist()
    pattern = re.compile("|".join(re.escape(n) for n in LEGACY))
    offenders: list[str] = []
    for path in _tracked_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in allow:
            continue
        # `.json` included deliberately. A legacy skill name is equally wrong in a
        # settings or manifest file, and omitting the suffix made this guard blind to
        # every `.json` in the repo -- `plugin.json`, `.vscode/settings.json`,
        # `.github/plugin/marketplace.json`.
        #
        # Worth being precise about what this does *not* fix, because it was reported
        # as the reason the stale `.vscode/settings.json` paths survived: it is not.
        # LEGACY holds two renamed *skill names*, and `skills/concierge` was never one
        # of them, so this pattern could not have matched that file at any suffix. The
        # guard that would have caught it is
        # `test_referenced_skill_paths_exist` below.
        if path.suffix not in {".md", ".py", ".yml", ".yaml", ".sh", ".txt", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if pattern.search(text):
            offenders.append(rel)
    assert not offenders, (
        "Legacy skill references found outside allowlist:\n  - "
        + "\n  - ".join(sorted(offenders))
    )


# ---------------------------------------------------------------------------
# Referenced skill paths must exist
# ---------------------------------------------------------------------------
#
# `.vscode/settings.json` pointed `chat.agentSkillsLocations` at `skills/concierge`,
# `skills/orchestrators`, `skills/execution` and `skills/document` for four months
# after the four-tier refactor flattened that layout away. Nothing noticed, and the
# failure was silent by construction: VS Code resolves what it can and reports
# nothing about what it cannot.
#
# The guard above could not have caught it at any suffix -- it matches two renamed
# skill *names*, and those four were directories. This is the missing check, and it
# is deliberately about the general shape rather than that one file: a tracked config
# that names a `skills/...` path which is not on disk is wrong regardless of which
# product reads it.

# Suffixes a machine reads as configuration. Prose is excluded on purpose: markdown
# legitimately names paths that do not exist yet, or once did, and a doc referring to
# a deleted directory is a documentation question rather than a broken pointer.
_CONFIG_SUFFIXES = {".json", ".yml", ".yaml"}

_SKILL_PATH = re.compile(r"^skills/[A-Za-z0-9_][A-Za-z0-9_./-]*$")


# Paths that are not configuration a product reads, and so cannot be stale in the
# sense this guard means.
#
# `graph.json` is generated. `tests/behavior/tests/fixtures/` holds synthetic inputs
# to the harness's *own* unit tests, and their old-layout paths are deliberate: they
# are asserted on by name in `test_cases_schema.py`
# (`assert case.skill == "skills/execution/discover-data"`), so "fixing" them would
# break the tests they exist for. They are arbitrary strings that happen to look like
# paths, which is exactly what a fixture is.
_NOT_CONFIG = ("tests/behavior/tests/fixtures/",)


def _config_files() -> list[Path]:
    out = []
    for p in _tracked_files():
        if p.suffix not in _CONFIG_SUFFIXES or p.name == "graph.json":
            continue
        rel = p.relative_to(REPO_ROOT).as_posix()
        if any(rel.startswith(prefix) for prefix in _NOT_CONFIG):
            continue
        out.append(p)
    return out


def _string_values(node: object) -> Iterator[str]:
    """Every string in a parsed document, at any depth."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str):
                yield key
            yield from _string_values(value)
    elif isinstance(node, (list, tuple)):
        for item in node:
            yield from _string_values(item)


def _skill_paths_in(path: Path) -> list[str]:
    """`skills/...` values in a config file, however the format quotes them.

    Parsed, not pattern-matched. The first version used
    `re.compile(r'"(skills/...)"')`, which only sees **double-quoted** strings --
    so the unquoted YAML scalar this repo actually uses in every behaviour case
    (`skill: skills/<name>`) was invisible to it, as was the single-quoted form. A
    guard against stale paths that cannot see the repo's own dominant spelling of
    those paths is close to useless.

    Parsing also means the check never matches a path inside a comment, which a
    regex over raw text would.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        if path.suffix == ".json":
            document = json.loads(text)
        else:
            document = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError):
        # An unparseable config is a different failure, reported by whatever reads
        # it. Silence here rather than a misattributed path finding.
        return []
    return [v for v in _string_values(document) if _SKILL_PATH.match(v)]


def test_there_are_config_files_to_check() -> None:
    """Without this the check below is a no-op that reports as a pass -- the same
    shape as the bug it exists to catch."""
    assert len(_config_files()) > 5


def test_every_format_family_actually_yields_paths() -> None:
    """Counting *files* is one level too coarse to notice a dead format.

    `len(_config_files()) > 5` is satisfied by the 19 JSON files on their own, so it
    stays green while the YAML half contributes nothing -- which is exactly the state
    this guard shipped in. The first `_skill_paths_in` matched only double-quoted
    strings, so all 136 behaviour cases (unquoted `skill: skills/<name>`) were
    invisible and a genuinely dead path in one of them passed.

    A/B against a mutant that makes the YAML branch return `[]`: without this test the
    whole module stays green *even with a dead path injected into a case file*; with
    it, the mutant fails here by name.

    Asserted per family rather than as a total, because a total is what hid it.
    `.yml` is deliberately absent from the expectation -- its 12 files are Databricks
    bundle templates and DAG fixtures with no `skills/` reference at all, verified by
    raw substring search, so requiring matches there would be requiring a fiction.
    """
    by_suffix: dict[str, int] = {}
    for path in _config_files():
        by_suffix[path.suffix] = by_suffix.get(path.suffix, 0) + len(_skill_paths_in(path))

    for suffix in (".json", ".yaml"):
        assert by_suffix.get(suffix, 0) > 0, (
            f"no skills/ paths were found in any {suffix} file, so that half of this "
            f"guard is inert. Either the repo genuinely stopped referencing skills "
            f"there, or _skill_paths_in cannot read {suffix} any more -- which is how "
            f"this check was born. Counts: {by_suffix}"
        )


def test_referenced_skill_paths_exist() -> None:
    offenders: list[str] = []
    for path in _config_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        for ref in _skill_paths_in(path):
            if not (REPO_ROOT / ref).exists():
                offenders.append(f"{rel} -> {ref}")

    assert not offenders, (
        "Config files name skills/ paths that do not exist. A path a product cannot "
        "resolve is silent -- it reports nothing and exposes nothing:\n  - "
        + "\n  - ".join(sorted(offenders))
    )
