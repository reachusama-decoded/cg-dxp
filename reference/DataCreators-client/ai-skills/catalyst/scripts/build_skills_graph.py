#!/usr/bin/env python3
"""Build the skills-graph dataset from SKILL.md frontmatter.

Source of truth: every ``skills/<name>/SKILL.md`` frontmatter block (RFD 0006) —
``metadata.tier``, ``metadata.lifecycle-phase``, ``metadata.dependencies``, and
``metadata.consumes``.  Agents are picked up from ``agents/<name>.md`` if that
directory ever exists; today it does not, and the graph simply renders zero of
them.

Target: ``docs/skills-graph/graph.json``, consumed by the sibling ``index.html``.

Output is deterministic — sorted keys, sorted edge lists, no timestamps — so the
``--check`` mode can be a byte-comparison and the file produces empty diffs when
nothing meaningful changed.

Usage:
  python scripts/build_skills_graph.py           # regenerate in place
  python scripts/build_skills_graph.py --check   # exit 1 if stale (CI mode)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
AGENTS_DIR = REPO_ROOT / "agents"
PLUGIN_JSON = REPO_ROOT / "plugin.json"
GRAPH_JSON = REPO_ROOT / "docs" / "skills-graph" / "graph.json"

# Directories under skills/ that are shared libraries, not skills.
EXCLUDED_DIRS = {"_lib", "assets", "clients", "core", "tests"}

# Lifecycle phase -> stage.  Stage drives node color (4 hues + neutral); phase
# drives horizontal lane order.  Keep in sync with skills/README.md.
PHASE_TO_STAGE = {
    "phase-0-prereq": "design",
    "phase-1-triage": "design",
    "phase-2-discovery": "design",
    "phase-3-design": "design",
    "phase-4-build": "build",
    "phase-5-validate": "build",
    "phase-6-publish": "build",
    "phase-7-operate": "ship",
    "phase-8-evolve": "ship",
    "cross-cutting": "cross-cutting",
    "none": "standalone",
}

# Lane order, left to right.  Phase is ordinal, so position carries the sequence
# and color is free to encode stage instead.
PHASE_ORDER = [
    "phase-0-prereq",
    "phase-1-triage",
    "phase-2-discovery",
    "phase-3-design",
    "phase-4-build",
    "phase-5-validate",
    "phase-6-publish",
    "phase-7-operate",
    "phase-8-evolve",
    "cross-cutting",
    "none",
]

PHASE_LABELS = {
    "phase-0-prereq": "0 · Prereq",
    "phase-1-triage": "1 · Triage",
    "phase-2-discovery": "2 · Discovery",
    "phase-3-design": "3 · Design",
    "phase-4-build": "4 · Build",
    "phase-5-validate": "5 · Validate",
    "phase-6-publish": "6 · Publish",
    "phase-7-operate": "7 · Operate",
    "phase-8-evolve": "8 · Evolve",
    "cross-cutting": "Cross-cutting",
    "none": "Standalone",
}

STAGE_LABELS = {
    "design": "Design",
    "build": "Build",
    "ship": "Ship",
    "cross-cutting": "Cross-cutting",
    "standalone": "Standalone",
}

VALID_TIERS = ("orchestrator", "workflow", "document", "capability")

# Five skills predate the RFD 0006 metadata block and omit tier and/or
# lifecycle-phase (tests/ci/test_skill_frontmatter_contract.py xfails them).
# The graph must not invent values for those — guessing "capability" would have
# rendered the dplc-validate orchestrator as a leaf.  They get UNSPECIFIED and
# the page flags them, so the gap is visible rather than papered over.
UNSPECIFIED = "unspecified"
GRAPH_TIERS = VALID_TIERS + (UNSPECIFIED,)

# A frontmatter `consumes` entry is sometimes a file artifact (dbt_project.yml,
# .env) rather than a sibling skill.  Those are real inputs but not graph edges;
# this spots them so they are reported rather than silently dropped.  Most carry
# a dot or a slash; the extensionless build files have to be named outright.
FILE_LIKE = re.compile(r"[/.]")
EXTENSIONLESS_ARTIFACTS = {"Dockerfile", "Makefile", "Procfile"}


def is_artifact(target: str) -> bool:
    """True when an unresolved edge target is a file, not a missing skill."""
    return bool(FILE_LIKE.search(target)) or target in EXTENSIONLESS_ARTIFACTS


def parse_frontmatter(md_path: Path) -> dict[str, Any]:
    """Return the YAML frontmatter block of a Markdown file as a dict."""
    content = md_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{md_path}: missing frontmatter delimiters")
    return yaml.safe_load(parts[1]) or {}


def first_sentence(text: str) -> str:
    """Collapse a description to a single sentence for the tooltip."""
    flat = " ".join((text or "").split())
    # Trigger-phrase lists are noise in a tooltip; cut them.
    flat = re.split(r"\s*Trigger phrases:", flat)[0]
    match = re.match(r"^(.*?[.!?])(?:\s|$)", flat)
    return (match.group(1) if match else flat).strip()


def registered_skills() -> set[str]:
    """Skill names registered in plugin.json."""
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    return {entry.rsplit("/", 1)[-1] for entry in plugin.get("skills", [])}


def collect_nodes() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return (nodes, raw_edges) harvested from skill and agent frontmatter."""
    registered = registered_skills()
    nodes: list[dict[str, Any]] = []
    raw_edges: list[dict[str, str]] = []

    sources: list[tuple[Path, str]] = [
        (d / "SKILL.md", "skill")
        for d in sorted(SKILLS_DIR.iterdir())
        if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "SKILL.md").exists()
    ]
    if AGENTS_DIR.is_dir():
        sources += [(p, "agent") for p in sorted(AGENTS_DIR.glob("*.md"))]

    for md_path, kind in sources:
        fm = parse_frontmatter(md_path)
        meta = fm.get("metadata") or {}
        name = fm.get("name") or md_path.parent.name

        gaps = sorted(f for f in ("tier", "lifecycle-phase") if not meta.get(f))

        phase = str(meta.get("lifecycle-phase") or "none")
        if phase not in PHASE_TO_STAGE:
            raise ValueError(
                f"{md_path}: unknown lifecycle-phase {phase!r}. "
                f"Add it to PHASE_TO_STAGE/PHASE_ORDER in {Path(__file__).name}."
            )

        tier = str(meta.get("tier") or UNSPECIFIED)
        nodes.append(
            {
                "id": name,
                "kind": kind,
                "tier": tier if tier in GRAPH_TIERS else UNSPECIFIED,
                "phase": phase,
                "stage": PHASE_TO_STAGE[phase],
                "description": first_sentence(fm.get("description", "")),
                "path": str(md_path.relative_to(REPO_ROOT)),
                "registered": kind == "agent" or name in registered,
                "gaps": gaps,
            }
        )

        for field, edge_type in (("dependencies", "composes"), ("consumes", "consumes")):
            for target in meta.get(field) or []:
                raw_edges.append({"source": name, "target": str(target), "type": edge_type})

    return sorted(nodes, key=lambda n: n["id"]), raw_edges


def build() -> dict[str, Any]:
    """Assemble the full graph document."""
    nodes, raw_edges = collect_nodes()
    known = {n["id"] for n in nodes}

    edges: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    for edge in raw_edges:
        if edge["target"] in known:
            edges.append(edge)
        else:
            # File artifacts are expected inputs; a non-file miss is a real
            # dangling reference and worth surfacing on the page.
            edge = dict(edge)
            edge["reason"] = "artifact" if is_artifact(edge["target"]) else "missing"
            unresolved.append(edge)

    # Deduplicate — a skill can name the same target in both fields.
    edges = [dict(t) for t in sorted({tuple(sorted(e.items())) for e in edges})]
    unresolved = [dict(t) for t in sorted({tuple(sorted(e.items())) for e in unresolved})]

    phases_present = [p for p in PHASE_ORDER if any(n["phase"] == p for n in nodes)]

    return {
        "$comment": (
            "GENERATED FILE — do not edit by hand. "
            "Run: python scripts/build_skills_graph.py"
        ),
        "schemaVersion": 1,
        "phases": [
            {"id": p, "label": PHASE_LABELS[p], "stage": PHASE_TO_STAGE[p]}
            for p in phases_present
        ],
        "stages": [
            {"id": s, "label": STAGE_LABELS[s]}
            for s in ("design", "build", "ship", "cross-cutting", "standalone")
        ],
        "tiers": list(GRAPH_TIERS),
        "nodes": nodes,
        "edges": edges,
        "unresolved": unresolved,
    }


def serialize(graph: dict[str, Any]) -> str:
    return json.dumps(graph, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main(check_only: bool = False) -> bool:
    graph = build()
    payload = serialize(graph)
    counts = (
        f"{len(graph['nodes'])} nodes, {len(graph['edges'])} edges, "
        f"{len(graph['unresolved'])} unresolved"
    )

    if check_only:
        if not GRAPH_JSON.exists():
            print(f"✗ {GRAPH_JSON.relative_to(REPO_ROOT)} is missing")
            print("  Run: python scripts/build_skills_graph.py")
            return False
        if GRAPH_JSON.read_text(encoding="utf-8") != payload:
            print(f"✗ {GRAPH_JSON.relative_to(REPO_ROOT)} is stale ({counts} expected)")
            print("  Run: python scripts/build_skills_graph.py")
            return False
        print(f"✓ skills graph is current ({counts})")
        return True

    GRAPH_JSON.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON.write_text(payload, encoding="utf-8")
    print(f"✓ Wrote {GRAPH_JSON.relative_to(REPO_ROOT)} ({counts})")
    for item in graph["unresolved"]:
        if item["reason"] == "missing":
            print(f"  ! {item['source']} → {item['target']} (no such skill)")
    for node in graph["nodes"]:
        if node["gaps"]:
            print(f"  ! {node['id']} has no {' or '.join(node['gaps'])} in frontmatter")
    return True


if __name__ == "__main__":
    sys.exit(0 if main(check_only="--check" in sys.argv) else 1)
