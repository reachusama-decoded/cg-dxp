# tests/behavior/cli.py
"""Argparse + main(). Per-case execution lives in dispatch.py."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

from tests.behavior.cases import ArtifactCase, load_cases
from tests.behavior.config import Config
from tests.behavior.dispatch import (
    _outcome_to_run,
    _print_job_result,
    _run_baseline_case,
    _run_case,
)
from tests.behavior.judge.rubric import RubricJudge
from tests.behavior.report import CaseOutcome, write_markdown
from tests.behavior.runner.claude_agent import ClaudeAgentRunner


def _cases_root() -> Path:
    override = os.getenv("BEHAVIOR_TESTS_CASES_ROOT")
    if override:
        return Path(override)
    return Path(__file__).parent / "cases"


def _is_fake() -> bool:
    return os.getenv("BEHAVIOR_TESTS_USE_FAKE_RUNNER") == "1"


def _build_runner_and_judge(config: Config):
    """Construct a runner + judge backed by claude-agent-sdk.

    Auth comes from Claude Code's session (or ANTHROPIC_API_KEY if set).
    Fake mode swaps in deterministic async iterators (see runner/fakes.py)
    that satisfy the structural checks and grade everything 1.0.
    """
    if _is_fake():
        from tests.behavior.runner.fakes import fake_judge_query, fake_runner_query
        runner = ClaudeAgentRunner(config=config, query_fn=fake_runner_query)
        judge = RubricJudge(config=config, query_fn=fake_judge_query)
        return runner, judge

    return ClaudeAgentRunner(config=config), RubricJudge(config=config)



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tests.behavior")
    parser.add_argument("--list", action="store_true", help="list discovered cases and exit")
    parser.add_argument("--skill", help="run only cases for this skill path (e.g. execution/discover-data)")
    parser.add_argument(
        "--case", action="append", default=[],
        help="run a specific case by id. Repeatable: --case A --case B. "
             "Comma-separated also works: --case A,B,C.",
    )
    parser.add_argument("--report", help="write a markdown report to this path")
    parser.add_argument("--runs", type=int, default=1, help="run each case N times for variance analysis (default 1)")
    parser.add_argument("--benchmark-dir", help="write skill-creator-compatible grading.json + benchmark.json into this directory")
    parser.add_argument(
        "--baseline", action="store_true",
        help="for each artifact case, also run a without_skill configuration; emit delta in benchmark.json",
    )
    parser.add_argument(
        "--live-report", metavar="DIR",
        help="write a self-refreshing HTML monitor (index.html + status.json) into DIR; "
             "open file://DIR/index.html in a browser before/during the run",
    )
    parser.add_argument(
        "--runner-model",
        help="model alias for the runner (e.g. claude-sonnet-4-6, claude-opus-4-7); "
             "default: claude-sonnet-4-6 or $BEHAVIOR_TESTS_RUNNER_MODEL",
    )
    parser.add_argument(
        "--judge-model",
        help="model alias for the judge; default: claude-sonnet-4-6 or $BEHAVIOR_TESTS_JUDGE_MODEL",
    )
    parser.add_argument(
        "--allowed-tools",
        help="comma-separated list of tools the runner is pre-authorized to call without "
             "interactive permission prompts (default: Bash,Read,Glob,Grep). Anything else "
             "still goes through the default permission flow — we do not bypass permissions.",
    )
    parser.add_argument(
        "--concurrency", type=int, default=1,
        help="run up to N cases in parallel (default 1). Each case spawns its own claude-agent-sdk session, "
             "so concurrency multiplies API/warehouse load — keep modest.",
    )
    parser.add_argument(
        "--cache-dir", metavar="DIR",
        help="record each case's runner output to DIR (one JSON per case+mode). "
             "Use with --from-cache later to re-judge without re-running.",
    )
    parser.add_argument(
        "--from-cache", metavar="DIR",
        help="re-judge cached runner outputs from DIR instead of executing the agent. "
             "Skips the runner entirely; only the judge is invoked. Useful when iterating on rubrics.",
    )
    parser.add_argument(
        "--allow-prod-databricks", action="store_true",
        help="acknowledge that DATABRICKS_HOST is a production workspace. Required when "
             "TEST_DATABRICKS_HOST is unset and you intentionally want a live run to hit "
             "the prod workspace. Without this flag, the CLI refuses to start.",
    )
    parser.add_argument(
        "--execute-only", action="store_true",
        help="Phase 1 of the two-phase pipeline: run the agent, cache the "
             "transcript, skip structural checks and the LLM judge. Use "
             "with --cache-dir to capture transcripts for later evaluation "
             "via --from-cache (= `bin/bt evaluate`).",
    )
    args = parser.parse_args(argv)
    if args.cache_dir and args.from_cache:
        parser.error("--cache-dir and --from-cache are mutually exclusive")
    if args.execute_only and args.from_cache:
        parser.error("--execute-only is for live runs (combine with --cache-dir, not --from-cache)")

    config = Config.from_env()
    if args.runner_model:
        config.runner_model = args.runner_model
    if args.judge_model:
        config.judge_model = args.judge_model
    if args.allowed_tools:
        config.allowed_tools = tuple(t.strip() for t in args.allowed_tools.split(",") if t.strip())

    # Databricks credential gate. The agent invokes Bash commands that read
    # DATABRICKS_HOST / DATABRICKS_TOKEN / DATABRICKS_WAREHOUSE_ID directly from
    # the subprocess environment — the Config object alone doesn't reach them.
    # If the user has set TEST_DATABRICKS_* explicitly, push those values into
    # os.environ as the canonical DATABRICKS_* so the subprocess sees them.
    # Honor BT_UNSET_VARS: a var listed there must NOT be re-injected — the
    # whole point is to test "what does the skill do when this is missing?"
    # If TEST_DATABRICKS_* are NOT set and a live run is requested against the
    # prod DATABRICKS_HOST, refuse — too easy to hit prod by accident.
    if not _is_fake() and not args.from_cache:
        unset_vars = set((os.getenv("BT_UNSET_VARS") or "").split())
        explicit_test = os.getenv("TEST_DATABRICKS_HOST")
        prod_host = os.getenv("DATABRICKS_HOST")
        if explicit_test and "DATABRICKS_HOST" not in unset_vars:
            os.environ["DATABRICKS_HOST"] = explicit_test
            if os.getenv("TEST_DATABRICKS_TOKEN") and "DATABRICKS_TOKEN" not in unset_vars:
                os.environ["DATABRICKS_TOKEN"] = os.environ["TEST_DATABRICKS_TOKEN"]
            if os.getenv("TEST_DATABRICKS_WAREHOUSE_ID") and "DATABRICKS_WAREHOUSE_ID" not in unset_vars:
                os.environ["DATABRICKS_WAREHOUSE_ID"] = os.environ["TEST_DATABRICKS_WAREHOUSE_ID"]
            print(f"[behavior-tests] using test workspace: {explicit_test}", file=sys.stderr)
        elif "DATABRICKS_HOST" in unset_vars:
            print(
                "[behavior-tests] DATABRICKS_HOST scrubbed via BT_UNSET_VARS; not re-injecting from TEST_*",
                file=sys.stderr,
            )
        elif prod_host and not args.allow_prod_databricks:
            print(
                f"[behavior-tests] refusing to run live against DATABRICKS_HOST={prod_host}\n"
                f"  Set TEST_DATABRICKS_HOST (and optionally TEST_DATABRICKS_TOKEN /\n"
                f"  TEST_DATABRICKS_WAREHOUSE_ID) to a non-production workspace, or pass\n"
                f"  --allow-prod-databricks if you really mean to run against prod.",
                file=sys.stderr,
            )
            return 2

    cases = load_cases(_cases_root())

    if args.skill:
        cases = [c for c in cases if c.skill.endswith(args.skill)]
    if args.case:
        # Flatten any comma-separated values within each --case occurrence
        wanted = {c.strip() for spec in args.case for c in spec.split(",") if c.strip()}
        missing = wanted - {c.id for c in cases}
        if missing:
            print(f"No cases match: {sorted(missing)}", file=sys.stderr)
            return 2
        cases = [c for c in cases if c.id in wanted]

    if args.list:
        for c in cases:
            print(f"{c.id}\t{c.skill}\t{c.type}")
        return 0

    if not cases:
        print("No cases matched.", file=sys.stderr)
        return 0

    # Live HTML monitor (optional)
    live = None
    if args.live_report:
        from tests.behavior.live_report import LiveReport
        plugin_skills: list[str] = []
        plugin_name = ""
        plugin_version = ""
        try:
            plugin_meta = json.loads(Path("plugin.json").read_text())
            plugin_skills = plugin_meta.get("skills", [])
            plugin_name = plugin_meta.get("name", "")
            plugin_version = plugin_meta.get("version", "")
        except Exception:
            pass
        live = LiveReport(
            output_dir=Path(args.live_report),
            cases=cases,
            all_skills=plugin_skills,
            config=config,
            suite_label=(args.skill or (",".join(args.case) if args.case else None) or "all"),
            runner_model=config.runner_model,
            judge_model=config.judge_model,
            plugin_name=plugin_name,
            plugin_version=plugin_version,
        )
        print(f"Live report: file://{Path(args.live_report).resolve()}/index.html")

    runner, judge = _build_runner_and_judge(config)

    # Wrap the runner if --cache-dir or --from-cache was set.
    cache_runner = None  # the CachingRunner / CachedRunner instance, if any
    if args.from_cache:
        from tests.behavior.runner.cache import CachedRunner
        # strict=False so cache misses become a clean error outcome instead
        # of crashing the whole run — users can see which cases lack cached
        # output in the report and decide what to re-run live.
        cache_runner = CachedRunner(cache_dir=Path(args.from_cache), strict=False)
        runner = cache_runner
    elif args.cache_dir:
        from tests.behavior.runner.cache import CachingRunner
        cache_runner = CachingRunner(inner=runner, cache_dir=Path(args.cache_dir))
        runner = cache_runner

    # Build the job list. Each job is (order_key, case, run_number, mode) where
    # order_key = (eval_id, run_number, mode_index) keeps the post-sort output stable.
    jobs: list[tuple[tuple[int, int, int], Any, int, str, int]] = []
    for eval_id, c in enumerate(cases, start=1):
        for run_number in range(1, args.runs + 1):
            jobs.append(((eval_id, run_number, 0), c, run_number, "with_skill", eval_id))
            if args.baseline and isinstance(c, ArtifactCase):
                jobs.append(((eval_id, run_number, 1), c, run_number, "without_skill", eval_id))

    def _execute(job) -> tuple[tuple[int, int, int], Any, int, str, int, CaseOutcome | None]:
        order_key, c, run_number, mode, eval_id = job
        if live:
            live.start_case(c.id)
        # Cache mode (None | "with_skill" | "without_skill") is passed
        # through to dispatch, which composes the transcript_id from the
        # case's skill + interpolated arguments. Concurrent _execute
        # calls each compute their own key — no shared state.
        cache_mode = mode if cache_runner is not None else None
        # Wrap dispatch in try/except so any unexpected exception (judge
        # SIGKILL, transport reset, JSON decode failure, etc.) becomes a
        # failure-with-error outcome instead of leaving the dashboard
        # stuck on "running" for this case. Without this, an exception in
        # _run_case causes finish_case to never be called — that was the
        # bug behind the lost-state for confluence-fetch on the prior run.
        try:
            if mode == "with_skill":
                outcome = _run_case(c, runner, judge, config,
                                    cache_mode=cache_mode,
                                    execute_only=args.execute_only)
            else:
                outcome = _run_baseline_case(c, runner, judge, config, cache_mode=cache_mode)
        except Exception as e:  # noqa: BLE001 — boundary handler is intentional
            outcome = CaseOutcome(
                case_id=c.id,
                passed=False,
                reason=f"runner error: {type(e).__name__}: {e}"[:300],
                weighted_score=None,
                duration_s=0.0,
                input_tokens=0,
                output_tokens=0,
                error=f"{type(e).__name__}: {e}"[:300],
            )
        if live and outcome is not None and mode == "with_skill":
            # Only update LiveReport from the with_skill leg — baseline is a
            # second pass on the same case_id and would clobber the visible row.
            live.finish_case(c.id, outcome)
        return order_key, c, run_number, mode, eval_id, outcome

    results: list[tuple[tuple[int, int, int], Any, int, str, int, CaseOutcome | None]] = []
    if args.concurrency <= 1:
        for job in jobs:
            results.append(_execute(job))
            order_key, c, run_number, mode, eval_id, outcome = results[-1]
            _print_job_result(c, run_number, args.runs, mode, outcome)
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(_execute, j): j for j in jobs}
            for fut in as_completed(futures):
                # Defense in depth: _execute already converts exceptions
                # to outcomes, but if anything else slips through (e.g., a
                # KeyboardInterrupt or a future cancelled mid-flight), keep
                # polling so we don't lose progress on the other 60+ cases.
                try:
                    tup = fut.result()
                except Exception as e:  # noqa: BLE001
                    job = futures[fut]
                    _, c, run_number, mode, eval_id = job
                    print(f"[error] {c.id}: {type(e).__name__}: {e}", file=sys.stderr)
                    continue
                results.append(tup)
                order_key, c, run_number, mode, eval_id, outcome = tup
                _print_job_result(c, run_number, args.runs, mode, outcome)

    # Sort to recover deterministic eval_id / run_number / mode ordering.
    results.sort(key=lambda r: r[0])

    outcomes: list[CaseOutcome] = []
    runs_collected: list = []
    failed = 0
    for _key, c, run_number, mode, eval_id, outcome in results:
        if outcome is None:
            continue  # baseline skipped (behavior case) — already logged
        config_label = "with_skill" if mode == "with_skill" else "without_skill"
        runs_collected.append(_outcome_to_run(c, outcome, config_label, run_number, eval_id))
        if mode == "with_skill":
            outcomes.append(outcome)
            if not outcome.passed:
                failed += 1

    if live:
        live.close()

    if args.report:
        write_markdown(Path(args.report), outcomes)
        print(f"Wrote report to {args.report}")

    if args.benchmark_dir:
        from tests.behavior.benchmark import emit_benchmark
        skill_name = (args.skill or "behavior-tests").replace("/", "-")
        emit_benchmark(runs_collected, Path(args.benchmark_dir), skill_name=skill_name)
        print(f"Wrote benchmark to {args.benchmark_dir}/benchmark.json")

    return 1 if failed else 0
