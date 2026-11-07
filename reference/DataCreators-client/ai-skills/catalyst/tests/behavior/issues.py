"""Generate GitHub issue bodies (and optionally file them) for each case
from the most recent behavior-test run.

Reads:
  workspace/behavior-tests/live-report/status.json   per-case status + reason
  workspace/behavior-tests/cache/<case>__with_skill.json   full transcript

Writes:
  workspace/behavior-tests/issues/<case-id>.md       one body per case

Two issue templates, distinguished by label and section structure:

  PASSED → "case review" — what the case verifies, run results, and
           seeded gap-analysis suggestions to refine into follow-up cases.
  FAILED → "failure dossier" — what the case verifies, why it failed,
           run evidence (tool-call timeline, output excerpt), seeded
           suggested-cause checklist tailored to the failure type.

Usage (from repo root):
  python -m tests.behavior.issues                  # dry run, write .md files only
  python -m tests.behavior.issues --create         # also `gh issue create` each one
  python -m tests.behavior.issues --case <id>      # restrict to one case
  python -m tests.behavior.issues --repo <owner>/<repo>   # default: gh's current

Issue creation requires the labels behavior-test:passed and
behavior-test:failed to exist; the helper prints the gh commands to
create them on first run.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

from tests.behavior.case_render import (
    render_grade_checklist,
    render_rubric_table,
    render_structural_checks,
)
from tests.behavior.runner.prompt_render import shorten_criterion_prompt  # noqa: F401  (kept for back-compat re-exports)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = REPO_ROOT / "workspace" / "behavior-tests"
CASES_ROOT = REPO_ROOT / "tests" / "behavior" / "cases"
ISSUES_DIR = WORKSPACE / "issues"

PASS_LABEL = "behavior-test:passed"
FAIL_LABEL = "behavior-test:failed"


def _first_release_skills() -> set[str]:
    """Skills enumerated in README.md under '### What's inside' (the
    current release scope), excluding 'What's not here (yet)' which
    lists staged Phase 4-8 skills.

    Parses the README rather than hardcoding so the scope tracks future
    edits to the readme without touching this file. Returns the bare
    skill names (e.g. {'discover-data', 'dplc-design', ...}), no
    `skills/` prefix.
    """
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        return set()
    text = readme.read_text()
    start = text.find("### What's inside")
    end = text.find("### What's not here", start)
    if start == -1 or end == -1:
        return set()
    section = text[start:end]
    # Skill names appear backticked in markdown tables and bullet lists;
    # they're lowercase + hyphenated. Filter out non-skill backticked
    # tokens (e.g. `plugin.json`, `skills/`) by requiring no dot/slash.
    candidates = re.findall(r"`([a-z][a-z0-9-]*)`", section)
    return {c for c in candidates if "." not in c and "/" not in c}


# ----------------------------------------------------------- repo metadata

def _git(*args: str) -> str:
    """One-shot git subprocess that returns stripped stdout."""
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def _repo_links(commit_sha: str, github_repo: str):
    """Return a function that builds permalink URLs at the given commit.
    Linking to the SHA (not a branch) makes the issue body durable across
    merges and branch deletes."""
    def _link(path: str, label: Optional[str] = None) -> str:
        label = label or path
        return f"[{label}](https://github.com/{github_repo}/blob/{commit_sha}/{path})"
    return _link


def _detect_github_repo() -> str:
    """Parse `git remote get-url origin` into 'owner/repo'. Falls back to
    a placeholder if the remote isn't a GitHub URL — issue creation will
    error in that case but the .md preview still works."""
    try:
        url = _git("remote", "get-url", "origin")
    except subprocess.CalledProcessError:
        return "owner/repo"
    # Forms: git@github.com:owner/repo.git, https://github.com/owner/repo(.git)
    for sep in ("github.com:", "github.com/"):
        if sep in url:
            tail = url.split(sep, 1)[1]
            return tail.removesuffix(".git").rstrip("/")
    return "owner/repo"


# --------------------------------------------------------------- loaders

def _load_status() -> dict[str, Any]:
    p = WORKSPACE / "live-report" / "status.json"
    if not p.exists():
        sys.exit(f"no status.json at {p} — run `bin/bt full` (or another live cmd) first.")
    state = json.loads(p.read_text())
    # Backfill plugin metadata from plugin.json when older runs didn't
    # capture it. Lets the issues helper version-label issues even from
    # in-flight or pre-versioning runs.
    if not state.get("plugin_name"):
        try:
            meta = json.loads((REPO_ROOT / "plugin.json").read_text())
            state["plugin_name"] = state.get("plugin_name") or meta.get("name", "")
            state["plugin_version"] = state.get("plugin_version") or meta.get("version", "")
        except Exception:
            pass
    return state


def _load_cache(case_state: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Cache files are content-addressed by `transcript_id` (skill+args
    hash), not case-id — a single transcript may back many cases. Read
    `transcript_id` from the per-case status entry (live_report writes
    it) and assemble the path from there."""
    tid = case_state.get("transcript_id")
    if not tid:
        return None
    p = WORKSPACE / "cache" / f"{tid}__with_skill.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _find_case_yaml(case_id: str) -> Optional[Path]:
    for path in CASES_ROOT.rglob("*.yaml"):
        try:
            d = yaml.safe_load(path.read_text())
        except yaml.YAMLError:
            continue
        if isinstance(d, dict) and d.get("id") == case_id:
            return path
    return None


# ------------------------------------------------------------- rendering

def _render_structural_checks(case: dict[str, Any]) -> str:
    return render_structural_checks(
        case.get("structural_checks") or [],
        expected_template=case.get("expected_template"),
        expected_components=case.get("expected_components") or [],
    )


def _render_rubric(case: dict[str, Any]) -> str:
    rubric = case.get("rubric")
    if not rubric:
        return "_(no rubric — behavior case)_"
    return render_rubric_table(rubric.get("threshold"), rubric.get("criteria", []))


def _render_pointers(case_id: str, case: dict[str, Any], case_yaml: Path, link) -> str:
    """Section with permalinks to the YAML, the SKILL.md, the template,
    and each expected component — pinned to the run's commit SHA."""
    rel_yaml = case_yaml.relative_to(REPO_ROOT).as_posix()
    skill_path = case.get("skill", "").rstrip("/")
    skill_md = f"{skill_path}/SKILL.md" if skill_path else None
    lines = [f"- **Case YAML:** {link(rel_yaml)}"]
    if skill_md:
        lines.append(f"- **Skill source:** {link(skill_md)}")
    if tmpl := case.get("expected_template"):
        lines.append(f"- **Expected template:** {link(tmpl)}")
    for comp in case.get("expected_components") or []:
        lines.append(f"- **Expected component:** {link(comp)}")
    return "\n".join(lines)


_render_grades = render_grade_checklist


def _render_coverage(case_state: dict[str, Any]) -> str:
    cov = case_state.get("coverage_summary") or {}
    if not cov.get("total"):
        return "_(no expected related skills/components declared)_"
    items = cov.get("items") or []
    pills = " · ".join(
        f"{'✅' if i['matched'] else '❌'} `{i['label']}`"
        for i in items
    )
    return f"**{cov['matched']}/{cov['total']} matched** — {pills}"


def _render_tool_timeline(cache: Optional[dict[str, Any]], limit: int = 30) -> str:
    if not cache:
        return "_(no transcript captured)_"
    lines = []
    for i, tc in enumerate(cache.get("tool_calls", [])[:limit], 1):
        args = tc.get("args") or {}
        if isinstance(args, dict):
            summary = (
                args.get("command")
                or args.get("file_path")
                or args.get("pattern")
                or args.get("skill")
                or args.get("path")
                or json.dumps(args)
            )
        else:
            summary = str(args)
        summary = str(summary).replace("\n", " ")[:200]
        lines.append(f"{i}. **{tc.get('name')}** — `{summary}`")
    extra = max(0, len(cache.get("tool_calls", [])) - limit)
    if extra:
        lines.append(f"… ({extra} more)")
    return "\n".join(lines) or "_(no tool calls)_"


def _render_output_excerpt(cache: Optional[dict[str, Any]], chars: int = 800) -> str:
    if not cache or not cache.get("output"):
        return "_(no output captured)_"
    text = cache["output"][:chars]
    suffix = "\n\n_…(truncated; see cache file for full output)_" if len(cache["output"]) > chars else ""
    return f"```markdown\n{text}{suffix}\n```"


# ---------------------------------------------------- gap-analysis seeds

def _gap_suggestions(case: dict[str, Any]) -> str:
    """Seed a checklist of additional cases worth considering, based on
    structural cues from the case YAML. Human refinement expected."""
    seeds: list[str] = []
    case_type = case.get("type", "artifact")
    args = case.get("input", {}).get("arguments", "")

    seeds.append("- [ ] **Empty / missing-input variant** — what does the skill produce when the request has no specific keywords or a known-empty domain? Does it surface 'no results' gracefully or hallucinate?")
    seeds.append("- [ ] **Ambiguous-input variant** — the same skill with a vague or multi-domain query. Does relevance scoring degrade cleanly or pick a wrong winner?")
    if case_type == "artifact":
        seeds.append("- [ ] **Adversarial structure variant** — runs that omit one prior-phase artifact the skill expects. Does the skill stub gracefully or fail loud?")
        if case.get("expected_template"):
            seeds.append("- [ ] **Partial-template variant** — does the skill cope when only a subset of template inputs are known? The current case is the happy path.")
        if case.get("expected_components"):
            seeds.append("- [ ] **Component-failure variant** — case where one expected component returns an error (e.g., warehouse offline). Does the skill report it or paper over?")
    if case_type == "behavior":
        seeds.append("- [ ] **Sub-skill failure variant** — case where one sub-skill reports a structural problem. Does the orchestrator re-route, retry, or stop?")
        seeds.append("- [ ] **Out-of-order variant** — case asserting that incorrect orderings still produce a coherent output (or fail explicitly).")
    if "${TEST_CATALOG}" in args or "${TEST_SCHEMA}" in args:
        seeds.append("- [ ] **Permission-denied variant** — table referenced is gated by Unity Catalog row-level security; verify the agent surfaces auth errors rather than data hallucinations.")
    seeds.append("- [ ] **Regression seeds** — capture the *current* run as a golden output and add a structural-diff check for future regressions.")
    return "\n".join(seeds)


# ----------------------------------------------------- cause heuristics

def _cause_suggestions(reason: str) -> str:
    """Seed a likely-cause checklist tailored to the failure surface."""
    r = reason.lower()
    items: list[str] = []
    if "matches_template" in r:
        items += [
            "- [ ] **SKILL.md doesn't explicitly read the template before drafting.** Add an early `Read templates/<doc>.md` step so the agent uses the canonical structure, not its own.",
            "- [ ] **Template has changed.** Verify the path in `expected_template` exists and that its H2 headings still reflect what authors should produce.",
            "- [ ] **Heading-extraction false negative.** The structural check looks for H2+ literal headings; nested H3s under a missing H2 won't help. Confirm the agent really skipped the section vs. nested it differently.",
        ]
    if "uses_components" in r:
        items += [
            "- [ ] **SKILL.md doesn't reference the layered component path explicitly.** Without an explicit `Read skills/core/<x>.py` (or import), the agent freelances and bypasses the layer.",
            "- [ ] **Component does the wrong thing.** If the agent tried it and got a confusing result, the layer may be the bug. Open the relevant `skills/core/<x>.py` and trace what the test fixture exercises.",
            "- [ ] **Naming drift.** Check whether the path in `expected_components` still exists at the expected location (recent refactors may have moved it).",
        ]
    if "missing expected sub-skills" in r:
        items += [
            "- [ ] **Orchestrator SKILL.md doesn't list the missing sub-skill as a step.** Without an explicit handoff, the agent skips it.",
            "- [ ] **Sub-skill prerequisites aren't met.** The orchestrator may be skipping the sub-skill because an earlier step that produces its inputs failed silently.",
            "- [ ] **Sub-skill runs with a different name in the registry.** Sub-skill detection accepts both `skills/<name>` and bare `<name>`; check whether the orchestrator wrote a third form.",
        ]
    if r.startswith("weighted"):
        items += [
            "- [ ] **Rubric is calibrated against an idealized output.** Pull the per-criterion grades and judge rationales; identify which criterion drove the weighted miss and decide whether the rubric or the skill is wrong.",
            "- [ ] **Judge non-determinism.** If the score is borderline, run with `--runs 3` to confirm it's not noise before changing anything.",
        ]
    if "runner error" in r or "max_turns" in r or "max_budget" in r:
        items += [
            "- [ ] **Skill is unbounded.** The agent looped or stalled — review the SKILL.md for ambiguous stop conditions.",
            "- [ ] **Sandbox/network blocked a needed resource.** Check the run log for `URLError` / sandbox denials around the time of failure.",
        ]
    if not items:
        items.append("- [ ] **Failure pattern not auto-classified.** Open the per-case `.md` in `workspace/behavior-tests/live-report/outputs/<case>.md` and inspect the tool-call timeline.")
    return "\n".join(items)


# --------------------------------------------------------- body builders

def _body_pass(case_id: str, case: dict[str, Any], state: dict[str, Any],
               run_state: dict[str, Any],
               cache: Optional[dict[str, Any]], case_yaml: Path, link) -> str:
    return f"""## Run context

{_run_context(run_state)}

## What this case verifies

**Skill:** `{case.get('skill')}`
**Type:** `{case.get('type')}`
**Description:** {case.get('description') or '_(no description in YAML)_'}

### Repo pointers
{_render_pointers(case_id, case, case_yaml, link)}

### Arguments
`{case.get('input', {}).get('arguments', '')}`

### Structural pre-checks
{_render_structural_checks(case)}

### Rubric
{_render_rubric(case)}

## Run results

**Status:** ✅ PASS
**Weighted score:** {f"{state['score']:.2f}" if state.get('score') is not None else '—'}
**Duration:** {state.get('duration_s') or 0:.1f}s
**Tokens:** {state.get('tokens', 0):,}

### Per-criterion grades
{_render_grades(state.get('criterion_grades') or [])}

### Expected Related Skills coverage
{_render_coverage(state)}

### Tool-call summary
{', '.join(f"`{k}`×{v}" for k, v in (state.get('tool_call_counts') or {}).items()) or '_(no tool calls)_'}

## Gaps to consider

What this case does **not** exercise. Use as a starter checklist for follow-up cases:

{_gap_suggestions(case)}

_Seeded from the case structure; please refine based on the SKILL.md and domain knowledge._

## How to re-run this case

```bash
# Live re-run, this case only (fast feedback, ~1–4 min):
bin/bt smoke {case_id}

# Same case 3× to characterize judge variance:
bin/bt run --case {case_id} --runs 3

# Re-judge the cached transcript without re-running the agent
# (cheap; useful when iterating on the rubric):
bin/bt rejudge --case {case_id}

# Schema-only dry run, no API/warehouse cost:
BEHAVIOR_TESTS_USE_FAKE_RUNNER=1 python -m tests.behavior --case {case_id}
```

Outputs land in `workspace/behavior-tests/`. Open
`file://$(pwd)/workspace/behavior-tests/live-report/index.html` to watch.
"""


def _body_fail(case_id: str, case: dict[str, Any], state: dict[str, Any],
               run_state: dict[str, Any],
               cache: Optional[dict[str, Any]], case_yaml: Path, link) -> str:
    return f"""## Run context

{_run_context(run_state)}

## What this case verifies

**Skill:** `{case.get('skill')}`
**Type:** `{case.get('type')}`
**Description:** {case.get('description') or '_(no description in YAML)_'}

### Repo pointers
{_render_pointers(case_id, case, case_yaml, link)}

### Arguments
`{case.get('input', {}).get('arguments', '')}`

### Structural pre-checks
{_render_structural_checks(case)}

### Rubric
{_render_rubric(case)}

## Why this failed

**Failure reason (verbatim):**
> {state.get('reason', '').strip() or '_(no reason recorded)_'}

## Run evidence

**Duration:** {state.get('duration_s') or 0:.1f}s
**Tokens:** {state.get('tokens', 0):,}
**Weighted score:** {f"{state['score']:.2f}" if state.get('score') is not None else '_(judge did not run — pre-check failed first)_'}

### Expected Related Skills coverage
{_render_coverage(state)}

### Tool-call timeline
{_render_tool_timeline(cache)}

### Output excerpt
{_render_output_excerpt(cache)}

## Possible causes & suggested next steps

{_cause_suggestions(state.get('reason', ''))}

_Seeded from the failure surface; please investigate the linked SKILL.md / template / components._

## How to re-run this case

```bash
# Live re-run, this case only:
bin/bt smoke {case_id}

# Same case 3× to confirm the fail isn't judge variance:
bin/bt run --case {case_id} --runs 3

# Re-judge the cached transcript (after the live re-run above)
# without re-executing the agent — useful for rubric iteration:
bin/bt rejudge --case {case_id}

# Schema-only dry run, no API/warehouse cost:
BEHAVIOR_TESTS_USE_FAKE_RUNNER=1 python -m tests.behavior --case {case_id}
```

After the re-run, the per-case detail page is at
`workspace/behavior-tests/live-report/outputs/{case_id}.md`
and the full transcript is in
`workspace/behavior-tests/cache/{case_id}__with_skill.json`.
"""


def _run_context(state: dict[str, Any]) -> str:
    """Top-of-issue 'this is what was tested' header — plugin@version,
    runner model, judge model, run timestamp. Pinned to the issue body
    so a reader can correlate against past runs."""
    rows = []
    if state.get("plugin_name"):
        rows.append(f"- **Plugin:** `{state['plugin_name']}@{state.get('plugin_version','?')}`")
    if state.get("runner_model"):
        rows.append(f"- **Runner model:** `{state['runner_model']}`")
    if state.get("judge_model"):
        rows.append(f"- **Judge model:** `{state['judge_model']}`")
    if state.get("started_at"):
        rows.append(f"- **Run started:** `{state['started_at']}`")
    return "\n".join(rows) or "_(no run context recorded)_"


# ----------------------------------------------------------------- main

def main() -> int:
    p = argparse.ArgumentParser(prog="tests.behavior.issues")
    p.add_argument("--case", action="append", default=[],
                   help="restrict to specific case id(s); repeatable")
    p.add_argument("--create", action="store_true",
                   help="actually `gh issue create` each generated body")
    p.add_argument("--repo",
                   help="<owner>/<repo> for issue creation; default: detected from origin remote")
    p.add_argument("--limit", type=int, default=None,
                   help="cap the number of issues created (sanity)")
    p.add_argument("--first-release", action="store_true",
                   help="only emit issues for skills listed in the README's "
                        "'What's inside' section (excludes Phase 4-8 staged skills)")
    p.add_argument("--include-runner-errors", action="store_true",
                   help="include cases that failed with a 'runner error' "
                        "(default: skip — they're usually harness bugs, not "
                        "skill signal, and shouldn't pollute the issue tracker)")
    args = p.parse_args()

    state = _load_status()
    sha = _git("rev-parse", "HEAD")
    repo = args.repo or _detect_github_repo()
    link = _repo_links(sha, repo)

    ISSUES_DIR.mkdir(parents=True, exist_ok=True)

    wanted = set(args.case) if args.case else None
    release_skills: Optional[set[str]] = None
    if args.first_release:
        release_skills = _first_release_skills()
        if not release_skills:
            print("could not extract first-release skills from README.md "
                  "(missing '### What's inside' section?)", file=sys.stderr)
            return 2
        print(f"--first-release scope: {len(release_skills)} skills "
              f"({', '.join(sorted(release_skills)[:5])}, …)\n")

    def _in_release(case_state: dict[str, Any]) -> bool:
        if release_skills is None:
            return True
        # case skill is "skills/<name>"; strip the prefix to compare.
        bare = case_state["skill"].rsplit("/", 1)[-1]
        return bare in release_skills

    def _is_runner_error(case_state: dict[str, Any]) -> bool:
        return (case_state["status"] == "failed"
                and "runner error" in (case_state.get("reason") or "").lower())

    eligible = [c for c in state["cases"]
                if c["status"] in ("passed", "failed")
                and (wanted is None or c["case_id"] in wanted)
                and _in_release(c)
                and (args.include_runner_errors or not _is_runner_error(c))]
    skipped_runner = [c for c in state["cases"]
                      if _is_runner_error(c) and _in_release(c)
                      and (wanted is None or c["case_id"] in wanted)
                      and not args.include_runner_errors]
    if skipped_runner:
        print(f"skipping {len(skipped_runner)} runner-error case(s) "
              "(harness, not skill — pass --include-runner-errors to surface):")
        for c in skipped_runner:
            print(f"  {c['case_id']}: {(c.get('reason') or '')[:80]}")
        print()
    if not eligible:
        print("no completed (passed/failed) cases match.", file=sys.stderr)
        return 0

    print(f"Repo: {repo}    Commit: {sha[:12]}")
    print(f"{len(eligible)} case(s) eligible "
          f"({sum(1 for c in eligible if c['status']=='passed')} passed, "
          f"{sum(1 for c in eligible if c['status']=='failed')} failed)")
    if args.create:
        print(f"--create active: will run `gh issue create` for each.")
        print(f"  ensure labels exist:")
        print(f"    gh label create {PASS_LABEL} -c '#0e8a16'")
        print(f"    gh label create {FAIL_LABEL} -c '#b60205'")
        if state.get("plugin_name"):
            v_label = f"version:{state['plugin_name']}-{state.get('plugin_version','?')}"
            print(f"    gh label create '{v_label}' -c '#1d76db'")
        print()

    created = 0
    for c in eligible:
        if args.limit and created >= args.limit:
            break
        case_id = c["case_id"]
        case_yaml = _find_case_yaml(case_id)
        if not case_yaml:
            print(f"  [skip] {case_id} — no case YAML found")
            continue
        case = yaml.safe_load(case_yaml.read_text())
        cache = _load_cache(c)
        passed = c["status"] == "passed"
        body = _body_pass(case_id, case, c, state, cache, case_yaml, link) if passed \
               else _body_fail(case_id, case, c, state, cache, case_yaml, link)
        title = (
            f"[behavior-test PASS] {case_id} — case review and gap analysis" if passed
            else f"[behavior-test FAIL] {case_id} — {(c.get('reason') or 'failed').splitlines()[0][:80]}"
        )
        out_path = ISSUES_DIR / f"{case_id}.md"
        out_path.write_text(f"# {title}\n\n{body}")
        if args.create:
            labels = [PASS_LABEL if passed else FAIL_LABEL]
            if state.get("plugin_name"):
                labels.append(f"version:{state['plugin_name']}-{state.get('plugin_version','?')}")
            cmd = ["gh", "issue", "create",
                   "--repo", repo,
                   "--title", title,
                   "--body-file", str(out_path)]
            for lab in labels:
                cmd += ["--label", lab]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"  [created] {case_id}: {r.stdout.strip()}")
            except subprocess.CalledProcessError as e:
                print(f"  [error]   {case_id}: {e.stderr.strip()}", file=sys.stderr)
        else:
            print(f"  [staged]  {case_id}  →  {out_path.relative_to(REPO_ROOT)}")
        created += 1

    if not args.create:
        print(f"\nDry run complete — {created} issue body file(s) staged in "
              f"{ISSUES_DIR.relative_to(REPO_ROOT)}/")
        print("Inspect a couple, then re-run with `--create` to file them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
