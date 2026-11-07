"""Skills-graph freshness check — the harness half of docs/skills-graph/.

``docs/skills-graph/graph.json`` is generated from every ``SKILL.md``
frontmatter block by ``scripts/build_skills_graph.py``.  The published page
reads that committed file directly, so a skill added, removed, renamed, or
re-phased without regenerating would leave the graph quietly wrong.

This test rebuilds the graph in memory and compares it to the committed copy,
which turns "remember to refresh the graph" into a failing check in the same
offline suite contributors already run:

    python -m pytest tests/ci tests/skills -q

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / "scripts" / "build_skills_graph.py"
GRAPH_JSON = REPO_ROOT / "docs" / "skills-graph" / "graph.json"
PAGE_HTML = REPO_ROOT / "docs" / "skills-graph" / "index.html"

REGEN = "Run: python scripts/build_skills_graph.py"


def _load_builder():
    """Import the generator by path — scripts/ is not an importable package."""
    spec = importlib.util.spec_from_file_location("build_skills_graph", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def builder():
    if not BUILDER.is_file():
        pytest.fail(f"missing generator: {BUILDER.relative_to(REPO_ROOT)}")
    return _load_builder()


# ---------------------------------------------------------------------------
# The freshness contract
# ---------------------------------------------------------------------------

def test_graph_json_exists():
    assert GRAPH_JSON.is_file(), f"{GRAPH_JSON.relative_to(REPO_ROOT)} is missing. {REGEN}"


def test_page_exists():
    assert PAGE_HTML.is_file(), f"{PAGE_HTML.relative_to(REPO_ROOT)} is missing."


def test_graph_json_matches_frontmatter(builder):
    """The committed graph is byte-identical to a fresh build."""
    expected = builder.serialize(builder.build())
    actual = GRAPH_JSON.read_text(encoding="utf-8")

    if actual == expected:
        return

    # Name the drift rather than dumping two 100-node blobs into the failure.
    try:
        old = json.loads(actual)
        new = json.loads(expected)
    except json.JSONDecodeError:
        pytest.fail(f"{GRAPH_JSON.relative_to(REPO_ROOT)} is not valid JSON. {REGEN}")

    old_ids = {n["id"] for n in old.get("nodes", [])}
    new_ids = {n["id"] for n in new.get("nodes", [])}
    added, removed = sorted(new_ids - old_ids), sorted(old_ids - new_ids)

    detail = []
    if added:
        detail.append(f"skills missing from the graph: {', '.join(added)}")
    if removed:
        detail.append(f"skills in the graph but gone from disk: {', '.join(removed)}")
    if not detail:
        n_old, n_new = len(old.get("edges", [])), len(new.get("edges", []))
        if n_old != n_new:
            detail.append(f"edge count changed: {n_old} committed vs {n_new} on disk")
        else:
            detail.append("skill metadata changed (tier, lifecycle-phase, or description)")

    pytest.fail(
        f"{GRAPH_JSON.relative_to(REPO_ROOT)} is stale — " + "; ".join(detail) + f". {REGEN}"
    )


def test_generator_check_mode_agrees(builder):
    """``--check`` must agree with the comparison above, since CI leans on it."""
    assert builder.main(check_only=True) is True, REGEN


# ---------------------------------------------------------------------------
# Internal consistency of the generated document
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def graph():
    return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))


def test_every_edge_resolves_to_a_node(graph):
    """A rendered edge with a dangling endpoint would draw to nowhere."""
    ids = {n["id"] for n in graph["nodes"]}
    dangling = [
        f"{e['source']} -> {e['target']}"
        for e in graph["edges"]
        if e["source"] not in ids or e["target"] not in ids
    ]
    assert not dangling, f"edges reference unknown skills: {dangling}"


def test_every_node_phase_has_a_band(graph):
    """A node whose phase has no band would be silently dropped from the page."""
    bands = {p["id"] for p in graph["phases"]}
    orphans = sorted({n["id"] for n in graph["nodes"] if n["phase"] not in bands})
    assert not orphans, f"skills whose lifecycle-phase has no band: {orphans}"


def test_every_node_tier_is_known(graph):
    """The page maps tier -> glyph; an unknown tier would render without one."""
    tiers = set(graph["tiers"])
    unknown = sorted({n["tier"] for n in graph["nodes"] if n["tier"] not in tiers})
    assert not unknown, f"skills with a tier the page cannot render: {unknown}"


def test_unresolved_targets_are_files_not_missing_skills(graph):
    """A `dependencies`/`consumes` entry naming a skill that does not exist.

    These are real frontmatter bugs — the skill points at something that was
    renamed or never existed. Files (dbt_project.yml, .env) are expected and
    classified separately by the generator.
    """
    missing = [
        f"{u['source']} -> {u['target']}"
        for u in graph.get("unresolved", [])
        if u.get("reason") == "missing"
    ]
    assert not missing, (
        "skills declare dependencies on non-existent skills: " + ", ".join(missing)
    )
