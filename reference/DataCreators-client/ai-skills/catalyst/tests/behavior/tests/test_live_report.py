"""Tests for the live HTML dashboard.

The renderer is pure: given a list of CaseSpecs and a sequence of
start_case/finish_case events, the resulting status.json + index.html
should be deterministic. These tests exercise the four state transitions
that matter — queued → running → passed/failed/skipped — plus atomicity.
"""
from __future__ import annotations
import json
from pathlib import Path

from tests.behavior.cases import ArtifactCase, Input, Rubric, Criterion
from tests.behavior.config import Config
from tests.behavior.live_report import LiveReport
from tests.behavior.report import CaseOutcome


def _config() -> Config:
    return Config.from_env()


def _make_case(case_id: str, skill: str = "skills/foo") -> ArtifactCase:
    return ArtifactCase(
        id=case_id,
        skill=skill,
        type="artifact",
        description="test",
        input=Input(arguments=""),
        rubric=Rubric(
            threshold=0.5,
            criteria=[Criterion(id="c", weight=1.0, prompt="ok?")],
        ),
    )


def _make_outcome(case_id: str, *, passed: bool = True, error: str | None = None) -> CaseOutcome:
    return CaseOutcome(
        case_id=case_id,
        passed=passed,
        reason="" if passed else "failed",
        weighted_score=0.9 if passed else 0.2,
        duration_s=1.5,
        input_tokens=100,
        output_tokens=50,
        error=error,
    )


class TestLiveReport:
    def test_initial_state_marks_all_cases_queued(self, tmp_path: Path):
        cases = [_make_case("a.case-01"), _make_case("b.case-01")]
        LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())

        state = json.loads((tmp_path / "status.json").read_text())
        assert state["totals"]["planned"] == 2
        assert state["totals"]["queued"] == 2
        assert state["totals"]["passed"] == 0

    def test_start_then_finish_passed(self, tmp_path: Path):
        cases = [_make_case("a.case-01")]
        live = LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())

        live.start_case("a.case-01")
        live.finish_case("a.case-01", _make_outcome("a.case-01", passed=True))

        state = json.loads((tmp_path / "status.json").read_text())
        assert state["totals"] == {
            "planned": 1, "passed": 1, "failed": 0, "skipped": 0,
            "running": 0, "queued": 0,
        }

    def test_finish_failed(self, tmp_path: Path):
        cases = [_make_case("a.case-01")]
        live = LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())

        live.start_case("a.case-01")
        live.finish_case("a.case-01", _make_outcome("a.case-01", passed=False))

        state = json.loads((tmp_path / "status.json").read_text())
        assert state["totals"]["failed"] == 1

    def test_cache_miss_classified_as_skipped_not_failed(self, tmp_path: Path):
        """Critical for --from-cache runs: cases without cached output should
        show as SKIP, not muddy the failure count."""
        cases = [_make_case("a.case-01")]
        live = LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())

        outcome = _make_outcome("a.case-01", passed=False, error="cache miss: no cached output")
        live.finish_case("a.case-01", outcome)

        state = json.loads((tmp_path / "status.json").read_text())
        assert state["totals"]["skipped"] == 1
        assert state["totals"]["failed"] == 0

    def test_per_case_md_written_on_finish(self, tmp_path: Path):
        cases = [_make_case("a.case-01")]
        live = LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())
        live.finish_case("a.case-01", _make_outcome("a.case-01", passed=True))

        case_md = tmp_path / "outputs" / "a.case-01.md"
        assert case_md.exists()
        assert "a.case-01" in case_md.read_text()

    def test_writes_are_atomic(self, tmp_path: Path):
        """No .tmp file should remain after a normal write — atomicity check."""
        cases = [_make_case("a.case-01")]
        live = LiveReport(output_dir=tmp_path, cases=cases, all_skills=[], config=_config())
        live.start_case("a.case-01")
        live.finish_case("a.case-01", _make_outcome("a.case-01"))

        # No leftover .tmp files
        leftovers = list(tmp_path.glob("*.tmp"))
        assert leftovers == [], f"leftover tmp files: {leftovers}"
        # Both files are valid (parseable JSON / non-empty HTML)
        assert json.loads((tmp_path / "status.json").read_text())
        assert "<html" in (tmp_path / "index.html").read_text()

    def test_coverage_panel_lists_untested_skills(self, tmp_path: Path):
        cases = [_make_case("a.case-01", skill="skills/foo")]
        all_skills = ["skills/foo", "skills/bar", "skills/baz"]
        LiveReport(output_dir=tmp_path, cases=cases, all_skills=all_skills, config=_config())

        state = json.loads((tmp_path / "status.json").read_text())
        assert state["coverage"]["tested"] == 1
        assert sorted(state["coverage"]["untested_skills"]) == ["skills/bar", "skills/baz"]
