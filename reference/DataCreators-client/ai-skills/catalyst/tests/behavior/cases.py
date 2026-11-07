# tests/behavior/cases.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Literal, Optional, Union
import yaml
from pydantic import BaseModel, Field, model_validator


class StructuralCheck(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, value: Any) -> "StructuralCheck":
        if isinstance(value, str):
            return cls(name=value)
        if isinstance(value, dict) and len(value) == 1:
            (name, arg_value), = value.items()
            if isinstance(arg_value, dict):
                return cls(name=name, args=arg_value)
            return cls(name=name, args={"name": arg_value} if name == "contains_section" else {"value": arg_value})
        raise ValueError(f"Invalid structural check: {value!r}")


class Criterion(BaseModel):
    id: str
    weight: float = Field(gt=0, le=1)
    prompt: str


class Rubric(BaseModel):
    threshold: float = Field(ge=0, le=1)
    criteria: list[Criterion] = Field(min_length=1)

    @model_validator(mode="after")
    def _weights_sum_to_one(self) -> "Rubric":
        total = sum(c.weight for c in self.criteria)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Rubric criterion weights must sum to 1.0, got {total}")
        return self


class Input(BaseModel):
    arguments: str


class Environment(BaseModel):
    databricks: Literal["live", "mocked", "not_required"] = "not_required"
    confluence: Literal["live", "mocked", "not_required"] = "not_required"


class _CaseBase(BaseModel):
    id: str
    skill: str
    description: str = ""
    input: Input
    environment: Environment = Field(default_factory=Environment)


class ArtifactCase(_CaseBase):
    type: Literal["artifact"]
    structural_checks: list[StructuralCheck] = Field(default_factory=list)
    rubric: Rubric
    # Architectural-conformance assertions, evaluated by the structural-check
    # tier (cheap, deterministic, before the LLM-judge runs).
    expected_template: Optional[str] = None
    """Repo-relative path to a markdown template (typically
    skills/<name>/templates/<doc>.md). The output must contain every H2
    heading and table-column-header set declared in the template — verifies
    the document's *structure*, not its content (the rubric handles content)."""

    expected_components: list[str] = Field(default_factory=list)
    """Repo-relative paths to layered components (capability skills, core
    modules, clients, etc.) the skill is expected to invoke. The harness
    scans the runner's tool-call args for each path; if any wasn't
    referenced, the case fails before the judge runs. Catches 'did
    discover-data actually use skills/core/discover.py and
    skills/clients/databricks.py, or did it freelance?'"""


class BehaviorCase(_CaseBase):
    type: Literal["behavior"]
    expected_sequence: list[str] = Field(min_length=1)
    strict_order: bool = True
    allow_extra: bool = True
    max_steps: int = Field(default=25, gt=0, le=200)
    expected_components: list[str] = Field(default_factory=list)
    """Same semantics as on ArtifactCase — verify the orchestrator (or any
    layered skill) actually invoked the expected underlying components."""


class Run(BaseModel):
    """A single agent execution: skill + arguments + environment.

    Defined once, referenced by N cases that evaluate orthogonal
    dimensions of the same output. Two cases that reference the same
    Run produce identical transcript_ids and share a cache entry — the
    first one runs the agent, the rest hit cache.

    YAML form (lives alongside cases, distinguished by `type: run`):

        type: run
        id: discover-data.run-01-happy-path
        skill: skills/discover-data
        input:
          arguments: "Inventory tables in ${TEST_CATALOG}.${TEST_SCHEMA} ..."
        environment:
          databricks: live

    Cases reference it via `run: <id>` instead of inlining skill+input.
    """
    type: Literal["run"]
    id: str
    skill: str
    input: Input
    environment: Environment = Field(default_factory=Environment)


CaseSpec = Union[ArtifactCase, BehaviorCase]


def parse_case(data: dict[str, Any]) -> CaseSpec:
    if "structural_checks" in data:
        data = dict(data)
        data["structural_checks"] = [StructuralCheck.from_yaml(c) for c in data["structural_checks"]]
    case_type = data.get("type")
    if case_type == "artifact":
        return ArtifactCase.model_validate(data)
    if case_type == "behavior":
        return BehaviorCase.model_validate(data)
    # Let pydantic produce the canonical error
    return ArtifactCase.model_validate(data)


def _resolve_run_reference(case_data: dict[str, Any], runs: dict[str, Run], path: Path) -> dict[str, Any]:
    """If a case YAML uses `run: <id>` instead of inlining skill+input,
    look up the referenced Run and copy skill/input/environment into the
    case dict before pydantic validation.

    Inlined fields on the case still win — lets a case override a Run's
    environment for one evaluation if needed (rare, but cheap to support).
    """
    run_id = case_data.get("run")
    if not run_id:
        return case_data
    run = runs.get(run_id)
    if run is None:
        raise ValueError(
            f"{path}: case references unknown run {run_id!r}. "
            f"Known runs: {sorted(runs.keys()) or '(none)'}"
        )
    merged = {
        "skill": run.skill,
        "input": run.input.model_dump(),
        "environment": run.environment.model_dump(),
        **case_data,  # case-local values override the run's defaults
    }
    merged.pop("run", None)
    return merged


def load_cases(root: Path) -> list[CaseSpec]:
    """Discover and parse every *.yaml under `root`, skipping fixtures/ subdirs.

    Two-pass: (1) collect Run definitions (`type: run`); (2) parse cases,
    resolving any `run: <id>` reference into inline skill+input fields.
    Run YAMLs and case YAMLs can live in the same directory tree.
    """
    runs: dict[str, Run] = {}
    case_entries: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(root.rglob("*.yaml")):
        if "fixtures" in path.parts:
            continue
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            raise ValueError(f"{path}: invalid YAML: {e}") from e
        if not isinstance(data, dict):
            raise ValueError(f"{path}: top-level YAML must be a mapping, got {type(data).__name__}")
        if data.get("type") == "run":
            try:
                run = Run.model_validate(data)
            except Exception as e:
                raise ValueError(f"{path}: invalid run: {e}") from e
            if run.id in runs:
                raise ValueError(f"Duplicate run id {run.id!r} (also at {path})")
            runs[run.id] = run
        else:
            case_entries.append((path, data))

    cases: list[CaseSpec] = []
    seen_ids: set[str] = set()
    for path, data in case_entries:
        try:
            data = _resolve_run_reference(data, runs, path)
            case = parse_case(data)
        except Exception as e:
            raise ValueError(f"{path}: invalid case: {e}") from e
        if case.id in seen_ids:
            raise ValueError(f"Duplicate case id {case.id!r} (also at {path})")
        seen_ids.add(case.id)
        cases.append(case)
    return cases
