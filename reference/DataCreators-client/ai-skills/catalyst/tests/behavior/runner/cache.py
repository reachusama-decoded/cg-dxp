"""Transcript cache for SkillRunner outputs.

Two wrappers around any SkillRunner:

  CachingRunner    saves each runner.run(...) result to disk before returning.
                   Use with `--cache-dir` to record a session for later reuse.

  CachedRunner     reads RunResult from disk; never executes the underlying agent.
                   Use with `--from-cache` to re-judge saved outputs (e.g. while
                   iterating on a rubric) without re-running the runner.

Cache layout (content-addressed):

  <cache_dir>/
    <transcript_id>__<mode>.json
        e.g. "skills_discover-data__a1b2c3d4__with_skill.json"

`transcript_id` is `<skill_safe>__<sha8(arguments + skill_body)>` so two
cases that test the *same* (skill, arguments, skill_body) tuple share a
single transcript on disk — the foundation for evaluating one transcript
against multiple rubrics. `mode` ("with_skill" / "without_skill") keeps
baseline runs from colliding with the main pass.

SKILL.md content is folded into the digest so editing a skill
auto-invalidates the cache: the next live run computes a new hash, the
old transcript stays on disk but is unreachable, and `bin/bt evaluate`
against a stale transcript reports "cache miss" (loud) instead of
silently re-judging a pre-edit run. Re-judging the rubric without
touching the skill still hits cache as intended — that workflow's
invariant is "skill stable, rubric changing", which the new key
respects.

The cache key arrives via the `cache_key` kwarg on `runner.run()`:
`(transcript_id, mode)` — opaque to the runner. The dispatch layer
computes the transcript_id from the case's `skill` + interpolated
`arguments` + current SKILL.md body and passes it in. Concurrent
workers never share state.
"""
from __future__ import annotations
import hashlib
import re
import threading
from pathlib import Path
from typing import Any, Optional

from tests.behavior.runner.base import CacheKey, RunResult, SkillRunner
from tests.behavior.runner.sub_skill_detection import (
    collect_sub_skills,
    count_self_invocations,
)

# Sanitize skill paths for use in filenames. Anything that isn't
# alphanumeric, dash, dot, or underscore becomes underscore.
_SKILL_FN_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def transcript_id(
    skill: str,
    arguments: str,
    *,
    skill_body: Optional[str] = None,
    system_override: Optional[str] = None,
    max_steps: Optional[int] = None,
) -> str:
    """Stable filename-safe identifier for the inputs that determine a run.

    Includes the skill path (sanitized) for human readability — when you
    grep the cache, you can see at a glance which skill a transcript came
    from. The hash digest disambiguates different argument values, the
    SKILL.md body (so a skill edit invalidates the cache), and any
    non-default `system_override` / `max_steps` so a baseline run or a
    different turn budget can't silently hit a cached transcript that
    was produced under different inputs.

    `skill_body` is optional so unit tests and other callers that don't
    have a real file on disk can omit it; the path-only key still works
    but loses auto-invalidation. Live dispatch always passes the body.

    Truncated to sha8 since a 1-in-a-billion accidental collision would
    just mean re-running one case live; not a security boundary.
    """
    safe_skill = _SKILL_FN_SAFE.sub("_", skill).strip("_")
    # Stable, ordered key/value form so the digest doesn't change just
    # because Python's dict insertion order shifts between callers.
    parts = [f"args={arguments}"]
    if skill_body is not None:
        body_hash = hashlib.sha256(skill_body.encode("utf-8")).hexdigest()[:16]
        parts.append(f"skill_body_sha={body_hash}")
    if system_override is not None:
        parts.append(f"system={system_override}")
    if max_steps is not None:
        parts.append(f"max_steps={max_steps}")
    payload = "\n".join(parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
    return f"{safe_skill}__{digest}"


def read_skill_body(skill_path: Path) -> Optional[str]:
    """Read the SKILL.md body for cache-key computation.

    Accepts either a path to a SKILL.md file (test fixtures) or to a
    skill directory containing one (the production case). Returns None
    if neither is found — transcript_id then falls back to the
    path-only key, which is the correct behavior for the few synthetic
    paths used in cache-module unit tests.
    """
    p = Path(skill_path)
    if p.is_file():
        return p.read_text(encoding="utf-8")
    md = p / "SKILL.md"
    return md.read_text(encoding="utf-8") if md.is_file() else None


def _cache_path(cache_dir: Path, transcript_id_: str, mode: str) -> Path:
    return cache_dir / f"{transcript_id_}__{mode}.json"


def save_run_result(cache_dir: Path, transcript_id_: str, mode: str, result: RunResult) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(cache_dir, transcript_id_, mode)
    path.write_text(result.model_dump_json(indent=2))
    return path


def load_run_result(cache_dir: Path, transcript_id_: str, mode: str) -> RunResult:
    path = _cache_path(cache_dir, transcript_id_, mode)
    if not path.exists():
        raise FileNotFoundError(
            f"no cached run result for transcript {transcript_id_!r} mode {mode!r} at {path}"
        )
    return RunResult.model_validate_json(path.read_text())


def _require_cache_key(runner_name: str, cache_key: Optional[CacheKey]) -> CacheKey:
    if cache_key is None:
        raise RuntimeError(
            f"{runner_name}.run called without cache_key=(transcript_id, mode)"
        )
    return cache_key


class CachingRunner(SkillRunner):
    """Decorator that memoizes runner.run output by content-addressed
    cache key. On cache hit, returns the saved RunResult without invoking
    the inner runner. On cache miss, invokes the inner runner, saves the
    result, and returns it.

    Two cases that share the same (skill, arguments) tuple now share the
    underlying transcript — the first one runs the agent, the rest hit
    cache. This is the dedup primitive that lets multiple cases evaluate
    orthogonal dimensions of the same output without re-running.

    To force a fresh run, point at a different `--cache-dir` or
    `bin/bt clean` first. SKILL.md edits auto-invalidate via the
    `skill_body` component of `transcript_id`.
    """

    def __init__(self, *, inner: SkillRunner, cache_dir: Path):
        self._inner = inner
        self._cache_dir = cache_dir
        # Per-(transcript_id, mode) lock prevents the thundering-herd
        # case: with concurrency > 1, three cases sharing a key all
        # check the cache *before* any has written → all three call the
        # agent. Serializing per-key keeps the first invocation honest;
        # the rest re-check cache after the lock and hit. Distinct keys
        # run in parallel (separate Lock instances).
        self._key_locks: dict[CacheKey, threading.Lock] = {}
        self._key_locks_guard = threading.Lock()

    def _key_lock(self, key: CacheKey) -> threading.Lock:
        with self._key_locks_guard:
            return self._key_locks.setdefault(key, threading.Lock())

    def run(
        self,
        skill_path: Path,
        arguments: str,
        max_steps: Optional[int] = None,
        system_override: Optional[str] = None,
        cache_key: Optional[CacheKey] = None,
    ) -> RunResult:
        transcript_id_, mode = _require_cache_key("CachingRunner", cache_key)
        with self._key_lock((transcript_id_, mode)):
            # Re-check cache *under the lock*. The first concurrent caller
            # may have already populated it while we were waiting.
            try:
                cached = load_run_result(self._cache_dir, transcript_id_, mode)
                sut = skill_path.parent.name if skill_path.suffix == ".md" else skill_path.name
                return cached.model_copy(update={
                    "sub_skills": collect_sub_skills(
                        cached.tool_calls, skill_under_test=sut,
                    ),
                    "self_invocations": count_self_invocations(
                        cached.tool_calls, skill_under_test=sut,
                    ),
                })
            except FileNotFoundError:
                pass
            result = self._inner.run(
                skill_path, arguments=arguments,
                max_steps=max_steps, system_override=system_override,
                cache_key=cache_key,
            )
            save_run_result(self._cache_dir, transcript_id_, mode, result)
            return result


class CachedRunner(SkillRunner):
    """Replacement runner: reads from cache, never invokes the agent.

    When `strict=True` (default), a missing cache file raises
    FileNotFoundError. When `strict=False`, a missing cache returns a
    RunResult with `error="cache miss: ..."` — useful from the CLI so
    the dashboard can list cache-miss cases without crashing the run.
    """

    def __init__(self, *, cache_dir: Path, strict: bool = True):
        self._cache_dir = cache_dir
        self._strict = strict

    def run(
        self,
        skill_path: Path,
        arguments: str,
        max_steps: Optional[int] = None,
        system_override: Optional[str] = None,
        cache_key: Optional[CacheKey] = None,
    ) -> RunResult:
        transcript_id_, mode = _require_cache_key("CachedRunner", cache_key)
        try:
            result = load_run_result(self._cache_dir, transcript_id_, mode)
        except FileNotFoundError as e:
            if self._strict:
                raise
            return RunResult(
                output="", tool_calls=[], sub_skills=[],
                duration_s=0.0, input_tokens=0, output_tokens=0,
                error=f"cache miss: {e}",
            )
        # Recompute sub_skills + self_invocations from tool_calls so
        # detection-rule changes apply when re-judging older caches.
        sut = skill_path.parent.name if skill_path.suffix == ".md" else skill_path.name
        return result.model_copy(update={
            "sub_skills": collect_sub_skills(result.tool_calls, skill_under_test=sut),
            "self_invocations": count_self_invocations(result.tool_calls, skill_under_test=sut),
        })
