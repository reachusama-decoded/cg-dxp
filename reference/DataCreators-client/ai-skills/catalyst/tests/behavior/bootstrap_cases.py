"""Bootstrap a happy-path case for every skill in plugin.json.

For each skill (`skills/<name>/SKILL.md`), emit a minimal case YAML at
`tests/behavior/cases/<name>/case-01-happy-path.yaml` if one doesn't
already exist. Existing cases are never overwritten.

Heuristics:
- **Behavior** vs **artifact**: if SKILL.md frontmatter `metadata.tier` is
  `orchestrator`, OR the skill name starts with `dplc-`, OR the body
  references "Sub-Skills Invoked" — emit a behavior case shell with an
  empty expected_sequence (TODO: hand-author).
- **expected_template**: if `skills/<name>/templates/<name>.md` exists, set it.
- **expected_components**: pull paths from a "Dependencies" section in
  SKILL.md if present (recognized prefixes: `skills/`).
- **arguments**: use the skill's `argument-hint` frontmatter; sub `${TEST_CATALOG}`
  for catalog placeholders.
- **rubric**: a generic 3-criterion baseline (request-addressed,
  format-conformant, no-placeholders). Hand-tune per skill afterwards.

Run with:
    python -m tests.behavior.bootstrap_cases [--force]
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent
CASES_ROOT = Path(__file__).parent / "cases"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
DEPENDENCIES_HEADING_RE = re.compile(
    r"^##\s+Dependencies\s*$(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL
)
DEP_PATH_RE = re.compile(r"`(skills/[^`]+\.py)`")


def _parse_skill(skill_path: Path) -> dict[str, Any]:
    text = skill_path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {"name": skill_path.parent.name, "description": "", "argument_hint": "", "body": text}
    import yaml
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return {
        "name": fm.get("name", skill_path.parent.name),
        "description": (fm.get("description") or "").strip(),
        "argument_hint": (fm.get("argument-hint") or "").strip(),
        "tier": (fm.get("metadata") or {}).get("tier") if isinstance(fm.get("metadata"), dict) else None,
        "body": body,
    }


def _find_template(skill_dir: Path) -> str | None:
    tpl_dir = skill_dir / "templates"
    if not tpl_dir.is_dir():
        return None
    candidates = sorted(tpl_dir.glob("*.md"))
    if not candidates:
        return None
    rel = candidates[0].relative_to(REPO)
    return str(rel)


def _detect_components(body: str) -> list[str]:
    m = DEPENDENCIES_HEADING_RE.search(body)
    if not m:
        return []
    block = m.group(1)
    paths = DEP_PATH_RE.findall(block)
    seen = set()
    out = []
    for p in paths:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out


def _is_behavior(skill_name: str, info: dict[str, Any]) -> bool:
    if info.get("tier") == "orchestrator":
        return True
    if skill_name.startswith("dplc-"):
        return True
    if "Sub-Skills Invoked" in info.get("body", ""):
        return True
    return False


def _format_arguments(arg_hint: str) -> str:
    """Heuristically substitute ${TEST_CATALOG} for catalog placeholders in
    the argument-hint, so the canned arguments work against the test
    catalog without manual editing."""
    if not arg_hint:
        return "<TODO: fill in arguments for this skill>"
    # Strip surrounding brackets, normalize whitespace
    cleaned = arg_hint.strip().strip("[]").strip()
    # Replace common catalog placeholders
    for ph in ("[catalog]", "<catalog>", "catalog"):
        if ph in cleaned:
            cleaned = cleaned.replace(ph, "${TEST_CATALOG}", 1)
            break
    return cleaned


def _artifact_case(skill_path: str, info: dict[str, Any], template: str | None,
                   components: list[str]) -> str:
    import yaml
    name = info["name"]
    description = info["description"][:300]
    arguments = _format_arguments(info["argument_hint"])
    data: dict[str, Any] = {
        "id": f"{name}.case-01-happy-path",
        "skill": skill_path,
        "type": "artifact",
        "description": f"Bootstrap happy-path case. {description}",
        "input": {"arguments": arguments},
        "structural_checks": ["non_empty_output", "no_placeholder_text"],
    }
    if template:
        data["expected_template"] = template
    if components:
        data["expected_components"] = components
    data["rubric"] = {
        "threshold": 0.7,
        "criteria": [
            {"id": "request_addressed", "weight": 0.4,
             "prompt": f"Does the output meaningfully address the request described by the skill: '{description[:140]}'? Score 0-1."},
            {"id": "format_conformant", "weight": 0.4,
             "prompt": "Does the output follow the structure the skill prescribes (sections, tables, fields, etc.)? Score 0-1."},
            {"id": "no_placeholders", "weight": 0.2,
             "prompt": "Output free of [TBD], [fill in], lorem-ipsum stubs, or empty cells where data was expected? Score 0-1."},
        ],
    }
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False, width=100)


def _behavior_case(skill_path: str, info: dict[str, Any]) -> str:
    import yaml
    name = info["name"]
    description = info["description"][:300]
    arguments = _format_arguments(info["argument_hint"])
    data = {
        "id": f"{name}.case-01-behavior",
        "skill": skill_path,
        "type": "behavior",
        "description": (
            f"Bootstrap behavior case. {description} "
            "TODO: fill in expected_sequence with the sub-skills this orchestrator "
            "should invoke before any document skill."
        ),
        "input": {"arguments": arguments},
        "expected_sequence": ["skills/TODO-first-sub-skill"],
        "strict_order": True,
        "allow_extra": True,
        "max_steps": 30,
    }
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False, width=100)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tests.behavior.bootstrap_cases")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing case files (default: skip)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what would be created, don't write")
    args = parser.parse_args(argv)

    plugin = json.loads((REPO / "plugin.json").read_text())
    skills: list[str] = plugin.get("skills", [])

    created, skipped, errored = 0, 0, 0
    for skill_path in skills:
        skill_dir = REPO / skill_path
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"⚠️  {skill_path} — SKILL.md not found, skipping")
            errored += 1
            continue

        info = _parse_skill(skill_md)
        skill_name = skill_dir.name
        case_dir = CASES_ROOT / skill_name
        case_kind = "behavior" if _is_behavior(skill_name, info) else "artifact"
        case_filename = (
            f"case-01-{'behavior' if case_kind == 'behavior' else 'happy-path'}.yaml"
        )
        case_path = case_dir / case_filename

        if case_path.exists() and not args.force:
            skipped += 1
            continue

        if case_kind == "behavior":
            content = _behavior_case(skill_path, info)
        else:
            template = _find_template(skill_dir)
            components = _detect_components(info["body"])
            content = _artifact_case(skill_path, info, template, components)

        if args.dry_run:
            print(f"[dry-run] would write {case_path}")
        else:
            case_dir.mkdir(parents=True, exist_ok=True)
            case_path.write_text(content)
            print(f"✓ {case_path.relative_to(REPO)}")
        created += 1

    print(f"\nCreated: {created} · Skipped (already exists): {skipped} · Errors: {errored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
