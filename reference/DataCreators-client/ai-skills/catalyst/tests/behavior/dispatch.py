"""Per-case execution + outcome construction.

Split out of cli.py because the original 580-line cli.py mixed argparse
with case-running logic. The flow:

  _run_case            artifact: runner → structural checks → rubric judge
                       behavior: runner → optional component check → sequence assertion
  _run_baseline_case   same as artifact branch but with system_override
                       (skipping structural checks; baseline is rubric-only)

  _outcome             single CaseOutcome construction site (used by every
                       early-return + the happy paths)
  _judge_against_rubric  load_skill + judge.score + _outcome — the rubric
                         flow shared by main and baseline runs

Plus the small helpers that gather observability fields (_tool_counts,
_tool_summary, _component_coverage, _grades_for_outcome) and the
benchmark-shape converter (_outcome_to_run).
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

from tests.behavior.cases import (
    ArtifactCase, BehaviorCase, StructuralCheck,
)
from tests.behavior.judge.sequence import (
    SequenceFailure, assert_sub_skill_sequence,
)
from tests.behavior.judge.structural import (
    StructuralCheckFailure, run_all, run_check,
)
from tests.behavior.report import CaseOutcome
from tests.behavior.runner.base import MaxStepsExceeded
from tests.behavior.runner.component_match import coverage
from tests.behavior.runner.skill_loader import load_skill

from tests.behavior.runner.cache import read_skill_body, transcript_id
from tests.behavior.runner.prompt_render import shorten_criterion_prompt

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

WITHOUT_SKILL_PROMPT = (
    "You are a helpful assistant. Respond directly to the user's request:\n\n$ARGUMENTS"
)


def _is_fake() -> bool:
    return os.getenv("BEHAVIOR_TESTS_USE_FAKE_RUNNER") == "1"


# --------------------------------------------------------- observability helpers

def _tool_counts(result):
    counts: dict[str, int] = {}
    for tc in result.tool_calls or []:
        counts[tc.name] = counts.get(tc.name, 0) + 1
    return counts


def _tool_summary(result):
    out = []
    for tc in result.tool_calls or []:
        args = tc.args or {}
        if tc.name == "Bash":
            summary = (args.get("command") or "")[:200]
        elif tc.name == "Skill":
            summary = (args.get("skill") or args.get("name")
                       or args.get("command") or str(args))[:200]
        elif tc.name in ("Read", "Glob", "Grep"):
            summary = (args.get("file_path") or args.get("pattern")
                       or args.get("path") or str(args))[:200]
        else:
            summary = str(args)[:200]
        out.append({"name": tc.name, "args": summary})
    return out


def _component_coverage(result, components):
    """Per-component verdict for the dashboard. Delegates to the shared
    `component_match` helper so the structural check and the dashboard
    agree on what 'used' means (output + tool args, not tool results)."""
    if not components:
        return []
    return coverage(
        components,
        tool_calls=result.tool_calls,
        output_text=result.output,
    )


# --------------------------------------------------------- outcome construction

def _outcome(
    case, result, *,
    passed: bool,
    reason: str = "",
    weighted_score: float | None = None,
    judge_input_tokens: int = 0,
    judge_output_tokens: int = 0,
    criterion_grades: list | None = None,
    error: str | None = None,
) -> CaseOutcome:
    """Build a CaseOutcome from a RunResult + judge decision. Centralizes
    the field-gathering so the seven different "return outcome" branches
    in _run_case / _run_baseline_case don't each hand-build it."""
    return CaseOutcome(
        case_id=case.id,
        passed=passed,
        reason=reason,
        weighted_score=weighted_score,
        duration_s=result.duration_s,
        input_tokens=result.input_tokens + judge_input_tokens,
        output_tokens=result.output_tokens + judge_output_tokens,
        criterion_grades=criterion_grades or [],
        error=error,
        output_text=result.output,
        tool_call_counts=_tool_counts(result),
        tool_calls_summary=_tool_summary(result),
        component_coverage=_component_coverage(result, getattr(case, "expected_components", [])),
        sub_skills=list(result.sub_skills or []),
    )


def _augment_structural_checks(case: ArtifactCase) -> list[StructuralCheck]:
    """Synthesize matches_template / uses_components / reads_exemplar
    checks from the case's architectural-conformance fields and from
    on-disk skill state. Returns the case's existing checks plus the
    synthesized ones.

    `reads_exemplar` is auto-derived: if the case's skill ships any
    `templates/example-*.md` files, the agent is expected to Read at
    least one (per SKILL.md step 2). Auto-discovery means new exemplars
    are picked up automatically without per-case YAML edits.
    """
    extra: list[StructuralCheck] = []
    if case.expected_template:
        extra.append(StructuralCheck(
            name="matches_template",
            args={"path": case.expected_template},
        ))
    if case.expected_components:
        extra.append(StructuralCheck(
            name="uses_components",
            args={"components": list(case.expected_components)},
        ))
    exemplars = _find_exemplars(case.skill)
    if exemplars:
        extra.append(StructuralCheck(
            name="reads_exemplar",
            args={"paths": exemplars},
        ))
    return list(case.structural_checks) + extra


def _find_exemplars(skill: str) -> list[str]:
    """Return repo-relative paths to any `templates/example-*.md` files
    under the given skill. Returns [] if the skill has no exemplars (so
    the synthesized check is a no-op for skills that haven't been given
    one yet)."""
    skill_dir = REPO_ROOT / skill / "templates"
    if not skill_dir.is_dir():
        return []
    return sorted(
        f"{skill}/templates/{p.name}" for p in skill_dir.glob("example-*.md")
    )


def _judge_against_rubric(case, result, judge, skill_path, arguments) -> CaseOutcome:
    """Score a runner result with the case's rubric and build the outcome.

    Single source for the rubric path used by both _run_case (artifact branch)
    and _run_baseline_case. Adding a field to the rubric flow now touches one
    place, not two.
    """
    skill = load_skill(skill_path, arguments=arguments)
    verdict = judge.score(
        rubric=case.rubric, output=result.output, skill_description=skill.description,
    )
    return _outcome(
        case, result,
        passed=verdict.passed,
        reason="" if verdict.passed else f"weighted={verdict.weighted_score:.2f}",
        weighted_score=verdict.weighted_score,
        judge_input_tokens=verdict.judge_input_tokens,
        judge_output_tokens=verdict.judge_output_tokens,
        criterion_grades=_grades_for_outcome(case.rubric.criteria, verdict),
    )


def _grades_for_outcome(criteria, verdict):
    """Convert per-criterion verdict grades into skill-creator-compatible expectations.

    The `text` field is what shows in dashboards / issue bodies / the
    skill-creator viewer — same shortener as the rubric table so a
    request_addressed grade line doesn't drown in an embedded skill
    description. The judge already saw the full prompt at scoring time.
    """
    PASS_FLOOR = 0.5  # per-criterion pass cutoff (rubric threshold is for weighted sum)
    out = []
    for crit, grade in zip(criteria, verdict.grades):
        prompt_short = shorten_criterion_prompt(crit.prompt or "")
        out.append({
            "text": f"{crit.id}: {prompt_short}",
            "passed": grade.score >= PASS_FLOOR,
            "evidence": f"score={grade.score:.2f}: {grade.rationale}",
        })
    return out




# --------------------------------------------------------- run_case dispatch

def _run_case(
    case, runner, judge, config,
    cache_mode: Optional[str] = None,
    execute_only: bool = False,
) -> CaseOutcome:
    """Dispatch a case end-to-end.

    `execute_only`: stop after the runner produces a transcript. Skip
    structural checks and the LLM judge. Used by `bin/bt execute` to do
    Phase 1 of the two-phase pipeline (transcripts now, evaluation
    later via `bin/bt evaluate`).
    """
    skill_path = REPO_ROOT / case.skill
    arguments = config.substitute(case.input.arguments, strict=not _is_fake())
    # Cache key is content-addressed by everything that affects the run:
    # skill path + interpolated args + current SKILL.md body, plus
    # max_steps for behavior cases (which vary the turn budget). The
    # skill body folded into the key means editing SKILL.md invalidates
    # the cache automatically. cache_mode is None when no --cache-dir /
    # --from-cache flag.
    case_max_steps = case.max_steps if isinstance(case, BehaviorCase) else None
    skill_body = read_skill_body(skill_path)
    cache_key = (
        transcript_id(
            case.skill, arguments,
            skill_body=skill_body, max_steps=case_max_steps,
        ),
        cache_mode,
    ) if cache_mode else None

    if execute_only:
        # Just run the agent and cache the transcript. No checks, no judge.
        # Both BehaviorCase and ArtifactCase land here uniformly — the
        # max_steps difference doesn't matter for transcript-only runs.
        try:
            if isinstance(case, BehaviorCase):
                result = runner.run(
                    skill_path, arguments=arguments,
                    max_steps=case.max_steps, cache_key=cache_key,
                )
            else:
                result = runner.run(skill_path, arguments=arguments, cache_key=cache_key)
        except MaxStepsExceeded as e:
            result = e.result
        return _outcome(
            case, result,
            passed=result.error is None,
            reason="executed (not graded — run `bin/bt evaluate` to score)"
                   if not result.error else f"runner error: {result.error}",
            error=result.error,
        )

    if isinstance(case, BehaviorCase):
        try:
            result = runner.run(
                skill_path, arguments=arguments,
                max_steps=case.max_steps, cache_key=cache_key,
            )
        except MaxStepsExceeded as e:
            result = e.result  # behavior cases tolerate early abort

        # max_turns and wall-clock are *cost caps*, not authoritative
        # pass/fail signals. Let the sequence assertion below be the judge:
        # if the agent stopped before invoking everything in expected_sequence,
        # SequenceFailure correctly fails the case with "missing expected
        # sub-skills: [...]" — far more actionable than "max_turns reached".
        # The one error we can't recover from is cache miss: no tool calls
        # captured, nothing to evaluate.
        unrecoverable = result.error and "cache miss" in result.error
        if unrecoverable:
            return _outcome(case, result, passed=False,
                            reason=f"runner error: {result.error}", error=result.error)
        if case.expected_components:
            try:
                run_check(
                    StructuralCheck(name="uses_components",
                                    args={"components": list(case.expected_components)}),
                    result.output,
                    tool_calls=result.tool_calls,
                )
            except StructuralCheckFailure as e:
                return _outcome(case, result, passed=False, reason=str(e))
        try:
            assert_sub_skill_sequence(
                result.sub_skills, case.expected_sequence,
                strict_order=case.strict_order, allow_extra=case.allow_extra,
                self_invocations=result.self_invocations,
            )
            return _outcome(case, result, passed=True,
                            reason=f"sub_skills={result.sub_skills}")
        except SequenceFailure as e:
            return _outcome(case, result, passed=False, reason=str(e))

    assert isinstance(case, ArtifactCase)
    result = runner.run(skill_path, arguments=arguments, cache_key=cache_key)
    if result.error:
        return _outcome(case, result, passed=False,
                        reason=f"runner error: {result.error}", error=result.error)
    try:
        run_all(_augment_structural_checks(case), result.output, tool_calls=result.tool_calls)
    except StructuralCheckFailure as e:
        return _outcome(case, result, passed=False, reason=str(e))
    return _judge_against_rubric(case, result, judge, skill_path, arguments)


def _run_baseline_case(case, runner, judge, config, cache_mode: Optional[str] = None) -> CaseOutcome | None:
    """Run an artifact case with the SKILL.md body replaced by a minimal prompt.

    Returns a CaseOutcome scored against the same rubric as the with_skill run.
    Behavior cases are not eligible — returns None.
    Structural checks are skipped for baseline (those are the skill author's expectations).
    """
    if not isinstance(case, ArtifactCase):
        return None
    skill_path = REPO_ROOT / case.skill
    arguments = config.substitute(case.input.arguments, strict=not _is_fake())
    # Baseline runs replace the skill body with WITHOUT_SKILL_PROMPT — fold
    # that into the transcript_id so a baseline can't silently hit a
    # with_skill cached transcript (or vice versa). skill_body is omitted
    # for baseline since the actual prompt is WITHOUT_SKILL_PROMPT, not the
    # SKILL.md body — including SKILL.md here would mean a skill edit
    # wrongly invalidates the matching baseline run too.
    cache_key = (
        transcript_id(case.skill, arguments, system_override=WITHOUT_SKILL_PROMPT),
        cache_mode,
    ) if cache_mode else None
    result = runner.run(
        skill_path, arguments=arguments,
        system_override=WITHOUT_SKILL_PROMPT, cache_key=cache_key,
    )

    if result.error:
        return _outcome(case, result, passed=False,
                        reason=f"baseline runner error: {result.error}", error=result.error)
    return _judge_against_rubric(case, result, judge, skill_path, arguments)


# --------------------------------------------------------- benchmark + printing

def _print_job_result(c, run_number: int, total_runs: int, mode: str, outcome) -> None:
    """Print one line per completed job. Called from both serial and parallel paths."""
    if outcome is None:
        print(f"  (skipping --baseline for behavior case {c.id})")
        return
    run_label = f" run {run_number}/{total_runs}" if total_runs > 1 else ""
    if mode == "with_skill":
        # `--execute-only` runs surface as EXEC instead of PASS so the user
        # can spot at a glance that grading was deferred.
        if outcome.passed and (outcome.reason or "").startswith("executed"):
            status = "EXEC"
        else:
            status = "PASS" if outcome.passed else "FAIL"
        print(f"[{status}] {outcome.case_id}{run_label}  ({outcome.duration_s:.1f}s)")
        if not outcome.passed:
            print(f"    {outcome.reason}")
    else:
        bstatus = "PASS" if outcome.passed else "FAIL"
        print(f"  [baseline {bstatus}] {c.id} without_skill score={outcome.weighted_score}")


def _outcome_to_run(case, outcome, configuration: str, run_number: int, eval_id: int):
    from tests.behavior.benchmark import BenchmarkRun
    if outcome.criterion_grades:
        grades = outcome.criterion_grades
    elif outcome.weighted_score is not None:
        grades = [{
            "text": "weighted rubric score >= threshold",
            "passed": outcome.passed,
            "evidence": f"score={outcome.weighted_score:.2f}",
        }]
    else:
        grades = [{
            "text": "case passed",
            "passed": outcome.passed,
            "evidence": outcome.reason or "",
        }]
    return BenchmarkRun(
        eval_id=eval_id, eval_name=case.id,
        configuration=configuration, run_number=run_number,
        outcome=outcome, criterion_grades=grades,
        tool_call_counts=dict(outcome.tool_call_counts or {}),
        output_chars=len(outcome.output_text or ""),
    )
