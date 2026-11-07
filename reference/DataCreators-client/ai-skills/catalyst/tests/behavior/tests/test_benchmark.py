# tests/behavior/tests/test_benchmark.py
import json
from pathlib import Path
import pytest

from tests.behavior.benchmark import (
    BenchmarkRun, emit_grading, emit_benchmark,
)
from tests.behavior.report import CaseOutcome


class TestEmitGrading:
    def test_writes_skill_creator_schema(self, tmp_path: Path):
        run = BenchmarkRun(
            eval_id=1,
            eval_name="discover-data.case-01-happy-path",
            configuration="with_skill",
            run_number=1,
            outcome=CaseOutcome(
                case_id="discover-data.case-01-happy-path",
                passed=True, reason="",
                weighted_score=0.85, duration_s=12.3,
                input_tokens=8000, output_tokens=2000,
            ),
            criterion_grades=[
                {"text": "structure: markdown table present", "passed": True, "evidence": "table found"},
                {"text": "groundedness: cg_employee_v4 referenced", "passed": True, "evidence": "row 2 lists cg_employee_v4"},
            ],
            tool_call_counts={"execute_sql": 3, "invoke_skill": 0},
        )
        out_dir = tmp_path / "eval-1" / "with_skill" / "run-1"
        out_dir.mkdir(parents=True)
        emit_grading(run, out_dir)
        data = json.loads((out_dir / "grading.json").read_text())
        # Exact field names per skill-creator schema
        assert "expectations" in data
        assert data["expectations"][0]["text"] == "structure: markdown table present"
        assert data["expectations"][0]["passed"] is True
        assert data["expectations"][0]["evidence"] == "table found"
        assert "summary" in data
        assert data["summary"]["passed"] == 2
        assert data["summary"]["pass_rate"] == 1.0
        assert "execution_metrics" in data
        assert data["execution_metrics"]["tool_calls"] == {"execute_sql": 3, "invoke_skill": 0}
        assert "timing" in data
        assert data["timing"]["total_duration_seconds"] == 12.3


class TestEmitBenchmark:
    def _make_run(self, eval_id: int, name: str, config: str, run_number: int, score: float, passed: bool):
        return BenchmarkRun(
            eval_id=eval_id, eval_name=name,
            configuration=config, run_number=run_number,
            outcome=CaseOutcome(
                case_id=name, passed=passed, reason="",
                weighted_score=score, duration_s=10.0,
                input_tokens=5000, output_tokens=1000,
            ),
            criterion_grades=[{"text": "x", "passed": passed, "evidence": ""}],
            tool_call_counts={},
        )

    def test_writes_benchmark_with_run_summary(self, tmp_path: Path):
        runs = [
            self._make_run(1, "case-A", "with_skill", 1, 0.9, True),
            self._make_run(1, "case-A", "with_skill", 2, 0.8, True),
            self._make_run(1, "case-A", "with_skill", 3, 0.7, False),
        ]
        emit_benchmark(runs, tmp_path, skill_name="discover-data")
        data = json.loads((tmp_path / "benchmark.json").read_text())
        assert data["metadata"]["skill_name"] == "discover-data"
        assert data["metadata"]["runs_per_configuration"] == 3
        assert len(data["runs"]) == 3
        assert data["runs"][0]["configuration"] == "with_skill"
        assert data["runs"][0]["result"]["pass_rate"] == 1.0
        assert "with_skill" in data["run_summary"]
        ws = data["run_summary"]["with_skill"]
        assert ws["pass_rate"]["mean"] == pytest.approx(0.6667, rel=1e-3)

    def test_includes_delta_when_baseline_present(self, tmp_path: Path):
        runs = [
            self._make_run(1, "case-A", "with_skill", 1, 0.9, True),
            self._make_run(1, "case-A", "without_skill", 1, 0.3, False),
        ]
        emit_benchmark(runs, tmp_path, skill_name="discover-data")
        data = json.loads((tmp_path / "benchmark.json").read_text())
        assert "with_skill" in data["run_summary"]
        assert "without_skill" in data["run_summary"]
        assert "delta" in data["run_summary"]

    def test_field_names_match_schema_exactly(self, tmp_path: Path):
        runs = [self._make_run(1, "case-A", "with_skill", 1, 0.9, True)]
        emit_benchmark(runs, tmp_path, skill_name="x")
        data = json.loads((tmp_path / "benchmark.json").read_text())
        # The viewer requires these exact field names — guard them.
        assert "config" not in data["runs"][0], "use 'configuration', not 'config'"
        assert "pass_rate" in data["runs"][0]["result"], "must be nested under 'result'"
        for required in ("eval_id", "eval_name", "configuration", "run_number", "result"):
            assert required in data["runs"][0], f"missing required field {required}"
