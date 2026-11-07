# tests/behavior/tests/test_cli.py
import os
import subprocess
import sys
import textwrap
from pathlib import Path
import pytest

WORKTREE_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def cases_root(tmp_path: Path) -> Path:
    target = tmp_path / "cases" / "execution" / "tiny-skill"
    target.mkdir(parents=True)
    (target / "case-01.yaml").write_text(textwrap.dedent("""\
        id: tiny-skill.case-01
        skill: tests/behavior/tests/fixtures/tiny_skill.md
        type: artifact
        description: Smoke test
        input:
          arguments: ""
        structural_checks:
          - non_empty_output
        rubric:
          threshold: 0.5
          criteria:
            - id: only
              weight: 1.0
              prompt: Non-empty? Score 0-1.
    """))
    return tmp_path / "cases"


class TestBehaviorCaseTolerateMaxSteps:
    """Regression for C1: behavior cases must tolerate max_turns / wall-clock
    early aborts. The captured sub_skills may already satisfy the expected
    sequence even when the runner ran out of budget — that's the whole point
    of MaxStepsExceeded carrying a partial result."""

    def test_max_steps_partial_result_with_matching_sequence_passes(self):
        from tests.behavior.cases import BehaviorCase, Input
        from tests.behavior.dispatch import _run_case
        from tests.behavior.config import Config
        from tests.behavior.runner.base import MaxStepsExceeded, RunResult

        case = BehaviorCase(
            id="t.case-01-behavior",
            skill="skills/tiny",
            type="behavior",
            description="x",
            input=Input(arguments=""),
            expected_sequence=["foo", "bar"],
            strict_order=False,
            allow_extra=True,
            max_steps=3,
        )

        partial = RunResult(
            output="partial", tool_calls=[],
            sub_skills=["foo", "bar"],
            duration_s=10.0, input_tokens=10, output_tokens=5,
            error="max_turns reached",  # set by runner before raising
        )

        class _RaisingRunner:
            def run(self, *a, **kw):
                raise MaxStepsExceeded("max_turns", result=partial)

        outcome = _run_case(case, _RaisingRunner(), judge=None, config=Config.from_env())
        assert outcome.passed, f"expected pass on partial-but-complete sequence; reason={outcome.reason!r}"

    def test_cache_miss_remains_unrecoverable(self):
        from tests.behavior.cases import BehaviorCase, Input
        from tests.behavior.dispatch import _run_case
        from tests.behavior.config import Config
        from tests.behavior.runner.base import RunResult

        case = BehaviorCase(
            id="t.case-01-behavior",
            skill="skills/tiny",
            type="behavior",
            description="x",
            input=Input(arguments=""),
            expected_sequence=["foo"],
            strict_order=False,
            allow_extra=True,
            max_steps=3,
        )

        class _CacheMissRunner:
            def run(self, *a, **kw):
                return RunResult(
                    output="", tool_calls=[], sub_skills=[],
                    duration_s=0.0, input_tokens=0, output_tokens=0,
                    error="cache miss: nothing on disk",
                )

        outcome = _run_case(case, _CacheMissRunner(), judge=None, config=Config.from_env())
        assert not outcome.passed
        assert "cache miss" in (outcome.reason or "")


class TestExecuteOnly:
    """Phase 1 of the two-phase pipeline: --execute-only runs the agent
    and caches the transcript without invoking structural checks or the
    LLM judge. Cases pass-through with reason="executed (not graded)".
    """

    def test_execute_only_skips_judge_and_caches_transcripts(
        self, cases_root: Path, tmp_path: Path
    ):
        cache = tmp_path / "cache"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--execute-only", "--cache-dir", str(cache)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        # Transcript was cached.
        assert list(cache.glob("*__with_skill.json")), "expected a cached transcript"
        # Output line shows EXEC (not PASS) so user knows grading was deferred.
        assert "[EXEC]" in result.stdout, result.stdout

    def test_execute_only_then_evaluate_round_trip(
        self, cases_root: Path, tmp_path: Path
    ):
        """Phase 1 (execute) → Phase 2 (--from-cache) actually grades the
        transcripts produced in phase 1."""
        cache = tmp_path / "cache"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        # Phase 1
        r1 = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--execute-only", "--cache-dir", str(cache)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert r1.returncode == 0, r1.stderr
        # Phase 2
        report = tmp_path / "report.md"
        r2 = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--from-cache", str(cache), "--report", str(report)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert r2.returncode == 0, r2.stderr
        assert "PASS" in report.read_text() or "FAIL" in report.read_text()

    def test_execute_only_with_from_cache_is_rejected(
        self, cases_root: Path, tmp_path: Path
    ):
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--execute-only", "--from-cache", str(tmp_path / "cache")],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "execute-only" in result.stderr.lower()


class TestExecuteBoundary:
    """Regression for the lost-dashboard-state issue (TODO #4): when
    `_run_case` raises (e.g., judge subprocess SIGKILLed mid-call), the
    case must still finish with a failure outcome and live.finish_case
    must be called — otherwise the dashboard shows 'running' forever
    and the case is excluded from issue/triage flows."""

    def test_runner_exception_becomes_failed_outcome_with_finish_case_called(
        self, cases_root: Path, tmp_path: Path, monkeypatch
    ):
        live_dir = tmp_path / "live"
        # Inject a _run_case that raises — simulates the judge crash that
        # caused the original lost-state bug.
        from tests.behavior import cli as cli_module

        def boom(*args, **kwargs):
            raise RuntimeError("simulated judge SIGKILL")
        monkeypatch.setattr(cli_module, "_run_case", boom)

        # In-process invocation so monkeypatch reaches main(). Use fake
        # mode so we don't hit Databricks for any other reason.
        monkeypatch.setenv("BEHAVIOR_TESTS_CASES_ROOT", str(cases_root))
        monkeypatch.setenv("BEHAVIOR_TESTS_USE_FAKE_RUNNER", "1")
        rc = cli_module.main([
            "--live-report", str(live_dir),
            "--concurrency", "1",
        ])
        assert rc == 1, "case should fail, not crash"

        import json
        state = json.loads((live_dir / "status.json").read_text())
        case = next(c for c in state["cases"] if c["case_id"] == "tiny-skill.case-01")
        assert case["status"] == "failed", f"expected failed, got {case['status']!r}"
        assert "simulated judge SIGKILL" in (case.get("reason") or "")


class TestCLI:
    def test_list_subcommand_shows_cases(self, cases_root: Path):
        env = {**os.environ, "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root)}
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior", "--list"],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "tiny-skill.case-01" in result.stdout

    def test_run_with_fake_writes_report(self, cases_root: Path, tmp_path: Path):
        report = tmp_path / "report.md"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior", "--report", str(report)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        body = report.read_text()
        assert "tiny-skill.case-01" in body
        assert "PASS" in body or "FAIL" in body


class TestBaselineMode:
    def test_baseline_emits_with_and_without_skill(self, cases_root: Path, tmp_path: Path):
        bench_dir = tmp_path / "bench"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--baseline", "--benchmark-dir", str(bench_dir)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        import json
        data = json.loads((bench_dir / "benchmark.json").read_text())
        configs = {r["configuration"] for r in data["runs"]}
        assert configs == {"with_skill", "without_skill"}
        assert "delta" in data["run_summary"]


@pytest.fixture
def multi_criterion_cases_root(tmp_path: Path) -> Path:
    target = tmp_path / "cases" / "execution" / "tiny-skill"
    target.mkdir(parents=True)
    (target / "case-01.yaml").write_text(textwrap.dedent("""\
        id: tiny-skill.multi-criterion
        skill: tests/behavior/tests/fixtures/tiny_skill.md
        type: artifact
        description: Multi-criterion smoke test
        input:
          arguments: ""
        structural_checks:
          - non_empty_output
        rubric:
          threshold: 0.5
          criteria:
            - id: structure
              weight: 0.3
              prompt: Structure ok?
            - id: groundedness
              weight: 0.4
              prompt: Grounded in real data?
            - id: clarity
              weight: 0.3
              prompt: Clear and concise?
    """))
    return tmp_path / "cases"


class TestPerCriterionGradesInBenchmark:
    """Regression test for code review C1: per-criterion grades must land in benchmark.json."""

    def test_benchmark_includes_one_expectation_per_rubric_criterion(
        self, multi_criterion_cases_root: Path, tmp_path: Path
    ):
        bench_dir = tmp_path / "bench"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(multi_criterion_cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--benchmark-dir", str(bench_dir)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        import json
        data = json.loads((bench_dir / "benchmark.json").read_text())
        assert len(data["runs"]) == 1
        expectations = data["runs"][0]["expectations"]
        # Three rubric criteria → three expectations, in the same order
        assert len(expectations) == 3, expectations
        ids = [e["text"].split(":")[0] for e in expectations]
        assert ids == ["structure", "groundedness", "clarity"]
        # Each expectation has the skill-creator schema fields
        for e in expectations:
            assert "text" in e
            assert "passed" in e
            assert "evidence" in e
            assert "score=" in e["evidence"]


@pytest.fixture
def many_cases_root(tmp_path: Path) -> Path:
    """Fixture with 4 distinct cases, used to verify --concurrency."""
    base = tmp_path / "cases" / "execution" / "tiny-skill"
    base.mkdir(parents=True)
    for i in range(1, 5):
        (base / f"case-{i:02d}.yaml").write_text(textwrap.dedent(f"""\
            id: tiny-skill.case-{i:02d}
            skill: tests/behavior/tests/fixtures/tiny_skill.md
            type: artifact
            description: Smoke test {i}
            input:
              arguments: ""
            structural_checks:
              - non_empty_output
            rubric:
              threshold: 0.5
              criteria:
                - id: only
                  weight: 1.0
                  prompt: Non-empty? Score 0-1.
        """))
    return tmp_path / "cases"


class TestConcurrency:
    def test_concurrency_runs_all_cases_with_stable_benchmark_order(
        self, many_cases_root: Path, tmp_path: Path
    ):
        bench_dir = tmp_path / "bench"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(many_cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--concurrency", "4", "--benchmark-dir", str(bench_dir)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        import json
        data = json.loads((bench_dir / "benchmark.json").read_text())
        # 4 cases × 1 run × 1 config = 4 runs, in eval_id order
        assert len(data["runs"]) == 4
        eval_ids = [r["eval_id"] for r in data["runs"]]
        assert eval_ids == sorted(eval_ids), f"benchmark.json runs not stably ordered: {eval_ids}"
        # All cases should have run
        names = sorted(r["eval_name"] for r in data["runs"])
        assert names == [
            "tiny-skill.case-01", "tiny-skill.case-02",
            "tiny-skill.case-03", "tiny-skill.case-04",
        ]


class TestTranscriptCache:
    def test_cache_dir_writes_cache_then_from_cache_skips_runner(
        self, cases_root: Path, tmp_path: Path
    ):
        """End-to-end: --cache-dir records, --from-cache reuses without rerunning the agent."""
        cache = tmp_path / "cache"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        # First pass: write cache.
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior", "--cache-dir", str(cache)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        cached_files = list(cache.glob("*.json"))
        assert len(cached_files) == 1, cached_files
        # Content-addressed cache key: <skill_safe>__<sha8>__<mode>.json.
        # tiny_skill case has arguments="" and no max_steps; the sha8
        # mixes "args=" with the SKILL.md body hash so a skill edit
        # auto-invalidates. See tests.behavior.runner.cache.transcript_id.
        from tests.behavior.runner.cache import read_skill_body, transcript_id
        fixture_path = WORKTREE_ROOT / "tests/behavior/tests/fixtures/tiny_skill.md"
        expected_tid = transcript_id(
            "tests/behavior/tests/fixtures/tiny_skill.md", "",
            skill_body=read_skill_body(fixture_path),
        )
        name = cached_files[0].name
        assert name.endswith("__with_skill.json"), name
        assert name.startswith(expected_tid + "__"), (
            f"expected transcript_id prefix {expected_tid}; got {name}"
        )

        # Second pass: read cache, no runner. Even with the fake runner removed
        # from the env, this should still succeed because we're loading from disk.
        env_no_fake = {**os.environ, "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root)}
        # We do still need the *judge* to run, so keep fake-runner mode (which
        # also fakes the judge); --from-cache only short-circuits the runner half.
        env_no_fake["BEHAVIOR_TESTS_USE_FAKE_RUNNER"] = "1"
        report = tmp_path / "report.md"
        result2 = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--from-cache", str(cache), "--report", str(report)],
            cwd=WORKTREE_ROOT, env=env_no_fake, capture_output=True, text=True,
        )
        assert result2.returncode == 0, result2.stderr
        body = report.read_text()
        assert "tiny-skill.case-01" in body

    def test_cache_dir_and_from_cache_mutually_exclusive(
        self, cases_root: Path, tmp_path: Path
    ):
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--cache-dir", str(tmp_path / "a"),
             "--from-cache", str(tmp_path / "b")],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "mutually exclusive" in result.stderr


class TestVarianceMode:
    def test_runs_N_produces_benchmark_with_N_runs_per_config(self, cases_root: Path, tmp_path: Path):
        bench_dir = tmp_path / "bench"
        env = {
            **os.environ,
            "BEHAVIOR_TESTS_CASES_ROOT": str(cases_root),
            "BEHAVIOR_TESTS_USE_FAKE_RUNNER": "1",
        }
        result = subprocess.run(
            [sys.executable, "-m", "tests.behavior",
             "--runs", "3", "--benchmark-dir", str(bench_dir)],
            cwd=WORKTREE_ROOT, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        import json
        data = json.loads((bench_dir / "benchmark.json").read_text())
        assert data["metadata"]["runs_per_configuration"] == 3
        # 1 case × 3 runs × 1 config (no --baseline) = 3 runs
        assert len(data["runs"]) == 3
        assert all(r["configuration"] == "with_skill" for r in data["runs"])
        assert "stddev" in data["run_summary"]["with_skill"]["pass_rate"]
