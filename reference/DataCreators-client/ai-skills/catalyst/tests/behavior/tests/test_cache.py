"""Transcript cache tests: CachingRunner / CachedRunner round-trip."""
from __future__ import annotations
import threading
from pathlib import Path
from typing import Any, Optional

import pytest

from tests.behavior.runner.base import RunResult, SkillRunner, ToolCall
from tests.behavior.runner.cache import (
    CachedRunner,
    CachingRunner,
    load_run_result,
    read_skill_body,
    save_run_result,
    transcript_id,
)


class TestTranscriptId:
    """Cache key is content-addressed by (skill, arguments) so cases that
    test the same input share a transcript on disk."""

    def test_same_skill_same_args_same_id(self):
        a = transcript_id("skills/discover-data", "find employee tables")
        b = transcript_id("skills/discover-data", "find employee tables")
        assert a == b

    def test_different_args_different_id(self):
        a = transcript_id("skills/discover-data", "find employee tables")
        b = transcript_id("skills/discover-data", "find product tables")
        assert a != b

    def test_skill_path_visible_in_id(self):
        """Human-readable prefix lets you grep the cache dir by skill."""
        tid = transcript_id("skills/discover-data", "X")
        assert tid.startswith("skills_discover-data__")

    def test_special_chars_in_skill_path_sanitized(self):
        tid = transcript_id("skills/foo bar/baz!", "X")
        # No spaces, no shell-special chars
        assert " " not in tid
        assert "!" not in tid

    def test_filename_safe(self):
        tid = transcript_id("skills/x/y", "weird ${VAR} input!")
        # Should be safe to use as a filename component on macOS/Linux/Windows
        for c in tid:
            assert c.isalnum() or c in "_-."

    def test_skill_body_changes_id(self):
        """Editing SKILL.md auto-invalidates the cache via the body hash.

        Without this, the runner returns a stale transcript and the
        smoke loop silently hits cache when iterating on a skill.
        """
        a = transcript_id("skills/x", "args", skill_body="version 1")
        b = transcript_id("skills/x", "args", skill_body="version 2")
        assert a != b

    def test_skill_body_none_matches_legacy_behavior(self):
        """Omitting `skill_body` keeps the path-only key shape so
        unit tests using synthetic skill paths still work."""
        a = transcript_id("skills/x", "args")
        b = transcript_id("skills/x", "args", skill_body=None)
        assert a == b

    def test_empty_skill_body_distinct_from_none(self):
        """`skill_body=""` (file exists but is empty) must hash distinctly
        from `skill_body=None` (no file). Both are valid states but mean
        different things — an empty SKILL.md should not collide with a
        path-only baseline key."""
        none_id = transcript_id("skills/x", "args", skill_body=None)
        empty_id = transcript_id("skills/x", "args", skill_body="")
        assert none_id != empty_id


class TestReadSkillBody:
    def test_reads_md_file_directly(self, tmp_path: Path):
        f = tmp_path / "skill.md"
        f.write_text("hello")
        assert read_skill_body(f) == "hello"

    def test_reads_skill_md_from_directory(self, tmp_path: Path):
        (tmp_path / "SKILL.md").write_text("dir-style skill")
        assert read_skill_body(tmp_path) == "dir-style skill"

    def test_returns_none_when_not_found(self, tmp_path: Path):
        assert read_skill_body(tmp_path / "does-not-exist") is None


class _StubRunner(SkillRunner):
    """Returns a deterministic RunResult; used to exercise the cache."""

    def __init__(self, output: str = "stub output"):
        self._output = output
        self.calls: list[tuple[Path, str]] = []

    def run(
        self,
        skill_path: Path,
        arguments: str,
        max_steps: Optional[int] = None,
        system_override: Optional[str] = None,
        cache_key: Any = None,
    ) -> RunResult:
        self.calls.append((skill_path, arguments))
        return RunResult(
            output=self._output,
            tool_calls=[ToolCall(name="Bash", args={"command": "echo hi"})],
            sub_skills=["sub-a"],
            duration_s=0.1,
            input_tokens=10,
            output_tokens=5,
        )


class TestSaveLoadRoundTrip:
    def test_save_then_load_recovers_run_result(self, tmp_path: Path):
        rr = RunResult(
            output="hello", tool_calls=[ToolCall(name="Read", args={"file_path": "/x"})],
            sub_skills=[], duration_s=2.0, input_tokens=1, output_tokens=2,
        )
        save_run_result(tmp_path, "demo.case-01", "with_skill", rr)
        loaded = load_run_result(tmp_path, "demo.case-01", "with_skill")
        assert loaded.output == "hello"
        assert loaded.tool_calls[0].name == "Read"
        assert loaded.input_tokens == 1

    def test_load_missing_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_run_result(tmp_path, "missing.case", "with_skill")

    def test_modes_separate_files(self, tmp_path: Path):
        rr_a = RunResult(output="A", tool_calls=[], sub_skills=[], duration_s=0, input_tokens=0, output_tokens=0)
        rr_b = RunResult(output="B", tool_calls=[], sub_skills=[], duration_s=0, input_tokens=0, output_tokens=0)
        save_run_result(tmp_path, "demo.case-01", "with_skill", rr_a)
        save_run_result(tmp_path, "demo.case-01", "without_skill", rr_b)
        assert load_run_result(tmp_path, "demo.case-01", "with_skill").output == "A"
        assert load_run_result(tmp_path, "demo.case-01", "without_skill").output == "B"


class TestCachingRunner:
    def test_calls_inner_and_writes_cache_on_miss(self, tmp_path: Path):
        inner = _StubRunner(output="real run")
        runner = CachingRunner(inner=inner, cache_dir=tmp_path)
        result = runner.run(Path("dummy"), arguments="", cache_key=("demo.case-01", "with_skill"))
        assert result.output == "real run"
        assert len(inner.calls) == 1
        loaded = load_run_result(tmp_path, "demo.case-01", "with_skill")
        assert loaded.output == "real run"

    def test_skips_inner_on_cache_hit(self, tmp_path: Path):
        """Memoization: second call with the same key reads from cache."""
        inner = _StubRunner(output="real run")
        runner = CachingRunner(inner=inner, cache_dir=tmp_path)
        runner.run(Path("dummy"), arguments="", cache_key=("demo.case-01", "with_skill"))
        runner.run(Path("dummy"), arguments="", cache_key=("demo.case-01", "with_skill"))
        # Inner should have been called exactly once across both calls.
        assert len(inner.calls) == 1

    def test_different_keys_each_call_inner_once(self, tmp_path: Path):
        """Distinct (skill, args) → distinct cache keys → no false dedup."""
        inner = _StubRunner(output="real run")
        runner = CachingRunner(inner=inner, cache_dir=tmp_path)
        runner.run(Path("dummy"), arguments="", cache_key=("demo.case-01", "with_skill"))
        runner.run(Path("dummy"), arguments="", cache_key=("demo.case-02", "with_skill"))
        assert len(inner.calls) == 2

    def test_run_without_cache_key_raises(self, tmp_path: Path):
        runner = CachingRunner(inner=_StubRunner(), cache_dir=tmp_path)
        with pytest.raises(RuntimeError, match="cache_key"):
            runner.run(Path("dummy"), arguments="")

    def test_concurrent_same_key_calls_inner_once(self, tmp_path: Path):
        """Thundering-herd regression: three concurrent runs of the same
        cache_key must result in exactly one call to the inner runner.
        Without the per-key lock, all three would race past the cache
        miss and each invoke the agent."""
        # Stub that blocks briefly so the race window is real.
        slow = _StubRunner(output="slow")
        # Track exactly-once.
        call_count = {"n": 0}
        original_run = slow.run

        def slow_run(skill_path, arguments, **kw):
            import time
            call_count["n"] += 1
            time.sleep(0.05)  # widen the race window
            return original_run(skill_path, arguments, **kw)
        slow.run = slow_run  # type: ignore[method-assign]

        runner = CachingRunner(inner=slow, cache_dir=tmp_path)
        barrier = threading.Barrier(3)

        def worker():
            barrier.wait()
            runner.run(Path("dummy"), arguments="",
                       cache_key=("shared.key", "with_skill"))

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert call_count["n"] == 1, (
            f"expected 1 inner call, got {call_count['n']} — per-key lock missing"
        )


class TestCachedRunner:
    def test_reads_cached_result_without_calling_agent(self, tmp_path: Path):
        rr = RunResult(
            output="cached", tool_calls=[], sub_skills=[],
            duration_s=1.5, input_tokens=20, output_tokens=10,
        )
        save_run_result(tmp_path, "demo.case-01", "with_skill", rr)

        runner = CachedRunner(cache_dir=tmp_path)
        result = runner.run(Path("dummy"), arguments="", cache_key=("demo.case-01", "with_skill"))
        assert result.output == "cached"
        assert result.duration_s == 1.5

    def test_missing_cache_raises(self, tmp_path: Path):
        runner = CachedRunner(cache_dir=tmp_path)
        with pytest.raises(FileNotFoundError):
            runner.run(Path("dummy"), arguments="", cache_key=("nonexistent.case", "with_skill"))


class TestConcurrentRuns:
    """With cache_key as a kwarg (not thread-local), two threads can hit the
    same runner concurrently with different keys and never race. This test
    used to verify thread-local correctness; now it verifies the simpler
    kwarg model has the same property automatically."""

    def test_concurrent_run_with_distinct_keys(self, tmp_path: Path):
        for i in range(2):
            save_run_result(
                tmp_path, f"demo.case-{i}", "with_skill",
                RunResult(output=f"out-{i}", tool_calls=[], sub_skills=[],
                          duration_s=0, input_tokens=0, output_tokens=0),
            )
        runner = CachedRunner(cache_dir=tmp_path)
        results: dict[str, str] = {}
        barrier = threading.Barrier(2)

        def worker(i: int):
            barrier.wait()  # both threads start runs simultaneously
            r = runner.run(
                Path("dummy"), arguments="",
                cache_key=(f"demo.case-{i}", "with_skill"),
            )
            results[f"thread-{i}"] = r.output

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert results["thread-0"] == "out-0"
        assert results["thread-1"] == "out-1"
