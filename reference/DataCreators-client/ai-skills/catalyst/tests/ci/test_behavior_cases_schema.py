"""Repo-wide behavior case YAML schema validation.

Every ``tests/behavior/cases/**/case-*.yaml`` file must parse via the
behavior harness without raising an exception.  Cases that use ``run: <id>``
references are resolved via the harness's ``load_cases`` helper, which performs
the two-pass (runs first, cases second) parsing.

Skills are auto-discovered via glob; no hardcoded file list.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import importlib.util
import pathlib
import typing
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Repo-wide case discovery
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

BEHAVIOR_CASE_FILES = sorted(
    (REPO_ROOT / "tests" / "behavior" / "cases").rglob("case-*.yaml")
)

# All skill subdirs that have at least one case-*.yaml
BEHAVIOR_CASE_DIRS = sorted(
    {f.parent for f in BEHAVIOR_CASE_FILES}
)


# ---------------------------------------------------------------------------
# Lazy loader for harness functions
# ---------------------------------------------------------------------------

def _load_cases_module():
    """Load cases.py from the behavior harness without module-name conflicts.

    Pytest inserts ``skills/`` into sys.path so ``import tests`` would resolve
    to ``skills/tests`` instead of the repo-root ``tests/`` package.
    We use importlib to load the file directly and rebuild Pydantic models.
    """
    import pydantic  # noqa: PLC0415

    cases_path = REPO_ROOT / "tests" / "behavior" / "cases.py"
    spec = importlib.util.spec_from_file_location("_behavior_cases_loader", cases_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    ns = {
        **vars(typing),
        **{k: v for k, v in mod.__dict__.items() if not k.startswith("__")},
    }
    for attr_name in list(mod.__dict__):
        attr = mod.__dict__.get(attr_name)
        if attr is None:
            continue
        try:
            if (
                isinstance(attr, type)
                and issubclass(attr, pydantic.BaseModel)
                and attr is not pydantic.BaseModel
            ):
                attr.model_rebuild(_types_namespace=ns)
        except Exception:
            pass

    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "case_file",
    BEHAVIOR_CASE_FILES,
    ids=lambda p: str(p.relative_to(REPO_ROOT / "tests" / "behavior" / "cases")),
)
def test_case_yaml_is_valid_mapping(case_file: pathlib.Path) -> None:
    """Top-level YAML structure must be a mapping."""
    raw = yaml.safe_load(case_file.read_text(encoding="utf-8"))
    assert isinstance(raw, dict), f"Top-level YAML must be a mapping, got {type(raw).__name__}"


@pytest.mark.parametrize(
    "skill_cases_dir",
    BEHAVIOR_CASE_DIRS,
    ids=lambda p: p.name,
)
def test_skill_cases_load_without_error(skill_cases_dir: pathlib.Path) -> None:
    """load_cases must succeed for every skill's cases directory.

    Using load_cases (rather than bare parse_case) correctly resolves
    ``run: <id>`` references before Pydantic validation.
    """
    mod = _load_cases_module()
    load_cases = mod.load_cases
    # load_cases raises on any parse error
    cases = load_cases(skill_cases_dir)
    assert cases, f"{skill_cases_dir.name}: load_cases returned no cases"
    rel = skill_cases_dir.relative_to(REPO_ROOT / "tests" / "behavior" / "cases")
    for case in cases:
        assert case.id, f"{rel}: case has empty id"
        assert case.skill, f"{rel}: case has empty skill"
