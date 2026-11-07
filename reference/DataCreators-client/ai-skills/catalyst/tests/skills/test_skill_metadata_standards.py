# tests/skills/test_skill_metadata_standards.py
"""Standards binding: every rule ID referenced in any skill's frontmatter
metadata.standards must exist in rfd/0008/standards.yaml. Wildcards
(`PY-AIRFLOW-*`) and ranges (`DBX-BUNDLE-001..010`) supported."""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
STANDARDS_YAML = REPO_ROOT / "rfd" / "0008" / "standards.yaml"

RULE_ID_PATTERN = re.compile(r"^([A-Z]+(?:-[A-Z]+)+)-(\d{3})$")
WILDCARD_PATTERN = re.compile(r"^([A-Z]+(?:-[A-Z]+)+)-\*$")
RANGE_PATTERN = re.compile(r"^([A-Z]+(?:-[A-Z]+)+)-(\d{3})\.\.(\d{3})$")


def _load_known_ids() -> set[str]:
    data = yaml.safe_load(STANDARDS_YAML.read_text())
    return {entry["id"] for entry in data.get("rules", [])}


def _expand(reference: str, known: set[str]) -> set[str]:
    if RULE_ID_PATTERN.match(reference):
        return {reference} if reference in known else set()
    m = WILDCARD_PATTERN.match(reference)
    if m:
        prefix = m.group(1) + "-"
        return {rid for rid in known if rid.startswith(prefix)}
    m = RANGE_PATTERN.match(reference)
    if m:
        prefix, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        return {f"{prefix}-{n:03d}" for n in range(lo, hi + 1)} & known
    return set()


def _skill_metadata_refs() -> dict[Path, list[str]]:
    refs: dict[Path, list[str]] = {}
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        text = skill_md.read_text()
        if "---" not in text:
            continue
        fm = text.split("---", 2)[1]
        try:
            data = yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            continue
        standards = (data.get("metadata") or {}).get("standards") or []
        if standards:
            refs[skill_md] = standards
    return refs


def test_every_standards_reference_resolves():
    known = _load_known_ids()
    bad: dict[str, list[str]] = {}
    for skill, refs in _skill_metadata_refs().items():
        for ref in refs:
            if RULE_ID_PATTERN.match(ref):
                if ref not in known:
                    bad.setdefault(str(skill), []).append(ref)
            elif WILDCARD_PATTERN.match(ref) or RANGE_PATTERN.match(ref):
                if not _expand(ref, known):
                    bad.setdefault(str(skill), []).append(ref)
            else:
                bad.setdefault(str(skill), []).append(f"malformed: {ref}")
    assert not bad, f"Unresolved standards references: {bad}"
