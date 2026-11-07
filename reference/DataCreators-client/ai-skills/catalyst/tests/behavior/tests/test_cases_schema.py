# tests/behavior/tests/test_cases_schema.py
from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError

from tests.behavior.cases import (
    ArtifactCase, BehaviorCase, parse_case,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestArtifactCaseSchema:
    def test_parses_artifact_fixture(self):
        data = yaml.safe_load((FIXTURES / "artifact_case.yaml").read_text())
        case = parse_case(data)
        assert isinstance(case, ArtifactCase)
        assert case.id == "discover-data.case-01-happy-path"
        assert case.skill == "skills/execution/discover-data"
        assert case.rubric.threshold == 0.75
        assert len(case.rubric.criteria) == 4
        assert sum(c.weight for c in case.rubric.criteria) == pytest.approx(1.0)

    def test_structural_checks_mixed_string_and_mapping(self):
        data = yaml.safe_load((FIXTURES / "artifact_case.yaml").read_text())
        case = parse_case(data)
        names = [c.name for c in case.structural_checks]
        assert "non_empty_output" in names
        assert "contains_section" in names
        section = next(c for c in case.structural_checks if c.name == "contains_section")
        assert section.args == {"name": "Discovered Tables"}

    def test_rubric_weights_must_sum_to_one(self):
        data = yaml.safe_load((FIXTURES / "artifact_case.yaml").read_text())
        data["rubric"]["criteria"][0]["weight"] = 0.5  # break it
        with pytest.raises(ValidationError, match="weights must sum to 1.0"):
            parse_case(data)


class TestBehaviorCaseSchema:
    def test_parses_behavior_fixture(self):
        data = yaml.safe_load((FIXTURES / "behavior_case.yaml").read_text())
        case = parse_case(data)
        assert isinstance(case, BehaviorCase)
        assert case.expected_sequence == [
            "skills/execution/discover-data",
            "skills/execution/data-profiling",
            "skills/document/feasibility-report",
        ]
        assert case.strict_order is True
        assert case.max_steps == 25


class TestCaseDispatch:
    def test_unknown_type_rejected(self):
        with pytest.raises(ValidationError, match="type"):
            parse_case({"id": "x", "skill": "y", "type": "bogus", "input": {"arguments": ""}})

    def test_missing_required_fields_rejected(self):
        with pytest.raises(ValidationError):
            parse_case({"id": "x"})
