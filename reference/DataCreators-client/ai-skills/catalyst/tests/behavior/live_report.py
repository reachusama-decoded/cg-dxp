"""Live HTML monitor for behavior-test runs.

Writes two files into a target directory:

  index.html    self-contained dashboard with embedded JSON state.
                Auto-refreshes every 3 seconds via <meta http-equiv="refresh">.
                Open with `file://...index.html` in a browser before/during
                a run.

  status.json   raw state, kept in sync with the HTML. Useful for debugging
                or ingest by other tools.

The runner calls `LiveReport.start_case(case_id)` before each run and
`LiveReport.finish_case(case_id, outcome)` after. The HTML has a JS
clock that advances elapsed-time client-side between meta-refreshes,
so we don't need a periodic Python tick.
"""
from __future__ import annotations
import html
import json
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from tests.behavior.case_render import (
    render_rubric_table,
    render_structural_checks,
)
from tests.behavior.cases import BehaviorCase, CaseSpec
from tests.behavior.config import Config
from tests.behavior.judge.sequence import normalize_skill as _normalize_skill
from tests.behavior.report import CaseOutcome
from tests.behavior.runner.cache import (
    read_skill_body as _read_skill_body,
    transcript_id as _transcript_id,
)

# Computed locally rather than imported from `dispatch` to avoid a
# latent circular-import risk; matches the convention used elsewhere
# in tests/ (see issues.py, runner/claude_agent.py).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class CaseProgress:
    case_id: str
    skill: str
    case_type: str
    description: str = ""
    arguments: str = ""
    case_yaml_path: Optional[str] = None
    status: str = "queued"          # queued | running | passed | failed
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    duration_s: Optional[float] = None
    score: Optional[float] = None
    reason: str = ""
    tool_call_counts: dict[str, int] = field(default_factory=dict)
    output_chars: int = 0
    tokens: int = 0
    # Expected vs actual coverage — surfaced inline in the dashboard so a
    # reviewer can spot "agent skipped feasibility-report" without opening
    # the per-case .md. Populated on init from the case spec; the *_observed
    # fields land at finish_case from the outcome.
    expected_sub_skills: list[str] = field(default_factory=list)
    observed_sub_skills: list[str] = field(default_factory=list)
    expected_components: list[str] = field(default_factory=list)
    component_coverage: list[dict[str, Any]] = field(default_factory=list)
    # Per-criterion judge grades — propagated into status.json so the
    # issues helper can render them without re-parsing the per-case .md.
    criterion_grades: list[dict[str, Any]] = field(default_factory=list)
    # Content-addressed transcript ID (skill+arguments hash). Cases that
    # share this value share a cache file and thus a single agent run —
    # surfaced in the dashboard so reviewers can see which evaluations
    # consume the same transcript.
    transcript_id: str = ""


class LiveReport:
    def __init__(
        self,
        output_dir: Path,
        cases: list[CaseSpec],
        all_skills: list[str],
        config: Config,
        suite_label: str = "behavior-tests",
        runner_model: str = "",
        judge_model: str = "",
        case_specs_by_id: Optional[dict[str, CaseSpec]] = None,
        plugin_name: str = "",
        plugin_version: str = "",
    ):
        self.dir = Path(output_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.suite_label = suite_label
        self.runner_model = runner_model
        self.judge_model = judge_model
        self.plugin_name = plugin_name
        self.plugin_version = plugin_version
        self.started_at = time.time()
        self._case_specs = case_specs_by_id or {c.id: c for c in cases}
        # Compute transcript_id off the *substituted* arguments so the
        # value matches what dispatch.py computes (and what the cache
        # filename actually uses). Fake-mode substitution is non-strict
        # so unset vars become empty rather than raising.
        fake = os.getenv("BEHAVIOR_TESTS_USE_FAKE_RUNNER") == "1"
        def _interp(arg: str) -> str:
            return config.substitute(arg, strict=not fake)
        # Resolve each skill path once and read SKILL.md body so the
        # transcript_id matches what dispatch.py computes (and what the
        # cache filename actually uses).
        self.progress: list[CaseProgress] = [
            CaseProgress(
                case_id=c.id,
                skill=c.skill,
                case_type=c.type,
                description=getattr(c, "description", "") or "",
                arguments=c.input.arguments,
                expected_sub_skills=list(getattr(c, "expected_sequence", []) or [])
                    if isinstance(c, BehaviorCase) else [],
                expected_components=list(getattr(c, "expected_components", []) or []),
                transcript_id=_transcript_id(
                    c.skill, _interp(c.input.arguments),
                    skill_body=_read_skill_body(REPO_ROOT / c.skill),
                    max_steps=c.max_steps if isinstance(c, BehaviorCase) else None,
                ),
            )
            for c in cases
        ]
        self.all_skills = sorted(all_skills)
        self.tested_skills = sorted({c.skill for c in cases})
        self.untested_skills = sorted(set(self.all_skills) - set(self.tested_skills))
        self.completed = False
        self._lock = threading.Lock()
        self._write()

    # ---------------------------------------------------------------- API

    def start_case(self, case_id: str) -> None:
        with self._lock:
            for p in self.progress:
                if p.case_id == case_id:
                    p.status = "running"
                    p.started_at = time.time()
                    break
            # Status flips to "running" but the rest of the data hasn't
            # changed; cheap status.json update is enough. The next
            # finish_case (or the throttle below) regenerates HTML.
            self._write(html_throttle=True)

    def finish_case(self, case_id: str, outcome: CaseOutcome) -> None:
        with self._lock:
            for p in self.progress:
                if p.case_id == case_id:
                    # Distinguish cache-miss skips from real failures so the
                    # dashboard doesn't read like every uncached case is broken.
                    if outcome.error and "cache miss" in outcome.error:
                        p.status = "skipped"
                    elif outcome.passed:
                        p.status = "passed"
                    else:
                        p.status = "failed"
                    p.finished_at = time.time()
                    p.duration_s = outcome.duration_s
                    p.score = outcome.weighted_score
                    p.reason = outcome.reason
                    p.tool_call_counts = dict(outcome.tool_call_counts or {})
                    p.output_chars = len(outcome.output_text or "")
                    p.tokens = outcome.input_tokens + outcome.output_tokens
                    p.observed_sub_skills = list(outcome.sub_skills or [])
                    p.component_coverage = list(outcome.component_coverage or [])
                    p.criterion_grades = list(outcome.criterion_grades or [])
                    break
            outputs_dir = self.dir / "outputs"
            outputs_dir.mkdir(exist_ok=True)
            case_doc_path = outputs_dir / f"{case_id}.md"
            case_spec = self._case_specs.get(case_id)
            case_doc_path.write_text(_render_case_doc(case_id, outcome, case_spec))
            self._write()

    def close(self) -> None:
        with self._lock:
            self.completed = True
            self._write()

    # --------------------------------------------------------- internal

    def _state(self) -> dict[str, Any]:
        return {
            "suite_label": self.suite_label,
            "runner_model": self.runner_model,
            "judge_model": self.judge_model,
            "plugin_name": self.plugin_name,
            "plugin_version": self.plugin_version,
            "started_at": datetime.fromtimestamp(
                self.started_at, tz=timezone.utc
            ).isoformat(),
            "elapsed_s": time.time() - self.started_at,
            "completed": self.completed,
            "totals": {
                "planned": len(self.progress),
                "passed": sum(1 for p in self.progress if p.status == "passed"),
                "failed": sum(1 for p in self.progress if p.status == "failed"),
                "skipped": sum(1 for p in self.progress if p.status == "skipped"),
                "running": sum(1 for p in self.progress if p.status == "running"),
                "queued": sum(1 for p in self.progress if p.status == "queued"),
            },
            "coverage": {
                "total_skills": len(self.all_skills),
                "tested": len(self.tested_skills),
                "untested": len(self.untested_skills),
                "tested_skills": self.tested_skills,
                "untested_skills": self.untested_skills,
            },
            "shared_transcripts": _shared_transcripts(self.progress),
            "cases": [
                {
                    "case_id": p.case_id,
                    "skill": p.skill,
                    "case_type": p.case_type,
                    "description": p.description,
                    "arguments": p.arguments,
                    "status": p.status,
                    "started_at": p.started_at,
                    "finished_at": p.finished_at,
                    "duration_s": p.duration_s,
                    "score": p.score,
                    "reason": p.reason,
                    "tool_call_counts": p.tool_call_counts,
                    "output_chars": p.output_chars,
                    "tokens": p.tokens,
                    "expected_sub_skills": p.expected_sub_skills,
                    "observed_sub_skills": p.observed_sub_skills,
                    "expected_components": p.expected_components,
                    "component_coverage": p.component_coverage,
                    "coverage_summary": _coverage_summary(p),
                    "criterion_grades": p.criterion_grades,
                    "transcript_id": p.transcript_id,
                }
                for p in self.progress
            ],
        }

    _html_min_interval_s = 1.0  # cap full-HTML rebuilds to ~1/sec

    def _write(self, *, html_throttle: bool = False) -> None:
        # Atomic write: write to .tmp then rename, so a browser polling at
        # 3s never reads a half-written file.
        # status.json is cheap and always rewritten. The HTML render is
        # the expensive path (full table + embedded JSON) — throttle it
        # for non-completion events so concurrency=N runs don't burn CPU
        # rebuilding the same page N times per second. The browser's
        # 3s meta-refresh still picks up the next state on its own cadence.
        state = self._state()
        self._atomic_write(self.dir / "status.json", json.dumps(state, indent=2))
        now = time.monotonic()
        if html_throttle and (now - getattr(self, "_last_html_at", 0.0)) < self._html_min_interval_s:
            return
        self._atomic_write(self.dir / "index.html", _render_html(state))
        self._last_html_at = now

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content)
        os.replace(tmp, path)


def _shared_transcripts(progress: list[CaseProgress]) -> list[dict[str, Any]]:
    """Groups of cases that share a transcript_id (≥ 2 cases each).

    Surfaced in the dashboard so a reviewer can see at a glance which
    evaluations consume the same agent run — the dedup primitive shipped
    in TODO #1 steps 1-3. Single-case transcripts (the common shape today)
    are filtered out to keep the panel signal-dense.
    """
    by_tid: dict[str, list[CaseProgress]] = {}
    for p in progress:
        if not p.transcript_id:
            continue
        by_tid.setdefault(p.transcript_id, []).append(p)
    out = []
    for tid, members in by_tid.items():
        if len(members) < 2:
            continue
        out.append({
            "transcript_id": tid,
            "skill": members[0].skill,
            "arguments": members[0].arguments,
            "case_ids": [m.case_id for m in members],
        })
    out.sort(key=lambda g: g["transcript_id"])
    return out


def _short(s: str, max_len: int = 36) -> str:
    """Compact a path for display in the coverage pill — keep the tail since
    'skills/core/discover.py' is more recognizable than 'skills/core/disc...'.
    """
    if len(s) <= max_len:
        return s
    return "…" + s[-(max_len - 1):]


def _coverage_items(p: CaseProgress) -> list[dict[str, Any]]:
    """Per-case expected-vs-actual list. Behavior cases use sub-skills;
    artifact cases with expected_components use those. Returns
    [{label, expected, matched}] with `matched` only meaningful once the
    case has finished."""
    out: list[dict[str, Any]] = []
    if p.expected_sub_skills:
        observed_norm = {_normalize_skill(s) for s in p.observed_sub_skills}
        for s in p.expected_sub_skills:
            label = _normalize_skill(s)
            out.append({
                "label": label,
                "kind": "sub-skill",
                "matched": label in observed_norm,
            })
    if p.expected_components:
        # component_coverage is the harness's authoritative match table;
        # fall back to "no data yet" for queued/running cases.
        cov_lookup = {c["component"]: c["matched"] for c in p.component_coverage}
        for comp in p.expected_components:
            out.append({
                "label": comp,
                "kind": "component",
                "matched": cov_lookup.get(comp, False),
            })
    return out


def _coverage_summary(p: CaseProgress) -> dict[str, Any]:
    """Compact 'matched/total' summary for the dashboard column. Returns
    {total, matched, items: [...]} or {total: 0} if the case has nothing
    to verify."""
    items = _coverage_items(p)
    matched = sum(1 for i in items if i["matched"])
    return {
        "total": len(items),
        "matched": matched,
        "items": items,
        # Status only meaningful once the case has finished — until then
        # observed lists are empty so matched/total looks like 0/N.
        "ready": p.status in ("passed", "failed", "skipped"),
    }


def _render_case_doc(case_id: str, outcome: CaseOutcome, case: Optional[CaseSpec] = None) -> str:
    """Per-case markdown: case definition + result + judge grades + runner output.

    Lives at <live-dir>/outputs/<case_id>.md so it can be opened directly
    from the dashboard or grepped from the shell.
    """
    grades_block = ""
    for g in outcome.criterion_grades or []:
        verdict = "PASS" if g.get("passed") else "FAIL"
        grades_block += f"\n### {verdict}: `{g.get('text', '')}`\n\n{g.get('evidence', '')}\n"

    tool_block = (
        ", ".join(f"{k}×{v}" for k, v in (outcome.tool_call_counts or {}).items())
        or "(no tool calls captured)"
    )

    # Render the case definition so the reader doesn't have to grep cases/.
    case_def = ""
    if case is not None:
        if hasattr(case, "rubric") and case.rubric:
            rubric_md = render_rubric_table(
                case.rubric.threshold,
                [{"id": c.id, "weight": c.weight, "prompt": c.prompt}
                 for c in case.rubric.criteria],
            )
        elif hasattr(case, "expected_sequence"):
            seq_lines = ["**Expected sub-skill sequence:**"]
            for s in case.expected_sequence:
                seq_lines.append(f"- `{s}`")
            seq_lines.append(
                f"  (strict_order={case.strict_order}, "
                f"allow_extra={case.allow_extra}, max_steps={case.max_steps})"
            )
            rubric_md = "\n".join(seq_lines)
        else:
            rubric_md = ""

        struct_md = (
            render_structural_checks(getattr(case, "structural_checks", []) or [])
            if hasattr(case, "structural_checks") else ""
        )
        struct_block = (
            f"**Structural pre-checks:**\n{struct_md}\n" if struct_md and struct_md != "_(none)_"
            else ""
        )

        case_def = f"""## What this case tests

**Skill under test:** `{case.skill}`
**Case type:** `{case.type}`
**Description:** {(getattr(case, 'description', '') or '').strip() or '—'}

**Arguments:** `{case.input.arguments}`

{struct_block}
{rubric_md}

"""

    # Component coverage (which expected components were referenced)
    coverage_block = ""
    if outcome.component_coverage:
        rows = "\n".join(
            f"| {'✅' if v['matched'] else '❌'} | `{v['component']}` |"
            for v in outcome.component_coverage
        )
        coverage_block = f"\n## Component coverage\n\n| Match | Expected component |\n|---|---|\n{rows}\n"

    # Tool-call timeline (per-call args, not just counts)
    timeline_block = ""
    if outcome.tool_calls_summary:
        steps = []
        for i, tc in enumerate(outcome.tool_calls_summary, 1):
            args_repr = tc['args'].replace('`', '\\`')
            steps.append(f"{i}. **{tc['name']}** — `{args_repr}`")
        timeline_block = f"\n## Tool-call timeline\n\n" + "\n".join(steps) + "\n"

    return f"""# {case_id}

**Status:** {'PASS' if outcome.passed else 'FAIL'}
**Score:** {f'{outcome.weighted_score:.2f}' if outcome.weighted_score is not None else '—'}
**Duration:** {outcome.duration_s:.1f}s
**Tokens:** {outcome.input_tokens + outcome.output_tokens:,} (in {outcome.input_tokens:,} / out {outcome.output_tokens:,})
**Tool calls:** {tool_block}
**Reason:** {outcome.reason or '—'}

{case_def}{coverage_block}{timeline_block}## Per-criterion grades
{grades_block or '(no grades — pre-check failed before judge ran)'}

## Runner output

```markdown
{outcome.output_text or '(no output captured)'}
```
"""


def _render_html(state: dict[str, Any]) -> str:
    """Produce a self-contained HTML page that displays `state`.

    Auto-refreshes every 3 seconds while the run is incomplete via
    `<meta http-equiv="refresh">`. Once the run is complete, refresh stops.
    """
    refresh_meta = (
        ""
        if state["completed"]
        else '<meta http-equiv="refresh" content="3">'
    )

    totals = state["totals"]
    coverage = state["coverage"]

    coverage_bar_pct = (
        round(100 * coverage["tested"] / coverage["total_skills"])
        if coverage["total_skills"]
        else 0
    )

    case_rows = []
    for c in state["cases"]:
        status_class = {
            "queued": "queued",
            "running": "running",
            "passed": "passed",
            "failed": "failed",
            "skipped": "skipped",
        }[c["status"]]
        status_label = c["status"].upper()
        if c["status"] == "running" and c["started_at"]:
            # JS-side clock so the counter ticks even when the file isn't rewritten
            status_label = (
                f'RUNNING (<span class="clock" data-started="{int(c["started_at"] * 1000)}">…</span>)'
            )
        score = (
            f"{c['score']:.2f}"
            if c["score"] is not None
            else "—"
        )
        duration = (
            f"{c['duration_s']:.1f}s"
            if c["duration_s"] is not None
            else "—"
        )
        tools = ", ".join(f"{k}×{v}" for k, v in c["tool_call_counts"].items()) or "—"
        # Linkable per-case detail document (only exists after the case finishes).
        case_link = (
            f' · <a href="outputs/{html.escape(c["case_id"])}.md">full output</a>'
            if c["status"] in ("passed", "failed", "skipped")
            else ""
        )

        # Coverage column: at-a-glance "expected sub-skills/components matched/total".
        # Inline pills show ✅/❌ per item so a reviewer can spot 'agent skipped
        # feasibility-report' without opening the per-case .md.
        cov = c.get("coverage_summary") or {"total": 0}
        if cov["total"] == 0:
            coverage_cell = '<span class="cov-none">—</span>'
        elif not cov.get("ready"):
            coverage_cell = (
                f'<span class="cov-pending">{cov["total"]} expected</span>'
            )
        else:
            cls = "cov-full" if cov["matched"] == cov["total"] else "cov-partial"
            badge = f'<span class="cov-badge {cls}">{cov["matched"]}/{cov["total"]}</span>'
            pills = "".join(
                f'<span class="cov-pill {"ok" if i["matched"] else "miss"}" '
                f'title="{html.escape(i["kind"])}: {html.escape(i["label"])}">'
                f'{"✅" if i["matched"] else "❌"} {html.escape(_short(i["label"]))}'
                f'</span>'
                for i in cov["items"]
            )
            coverage_cell = f'{badge}<div class="cov-pills">{pills}</div>'

        # Inline expandable details — visible for queued/running cases too,
        # so the user can see what each case tests without grepping cases/.
        description = (c.get("description") or "").strip() or "(no description)"
        arguments = c.get("arguments") or ""
        # data-case-key lets JS persist open state across the meta-refresh
        details_block = f"""
            <details class="case-details" data-case-key="{html.escape(c['case_id'])}">
                <summary>show what this case tests</summary>
                <div class="details-body">
                    <div><strong>Description:</strong> {html.escape(description)}</div>
                    <div><strong>Arguments:</strong> <code>{html.escape(arguments)}</code></div>
                </div>
            </details>
        """

        # status_label may contain HTML for the JS clock — don't escape it.
        case_rows.append(
            f"""<tr class="{status_class}">
                <td><span class="badge {status_class}">{status_label}</span></td>
                <td><code>{html.escape(c['case_id'])}</code>{case_link}{details_block}</td>
                <td><code>{html.escape(c['skill'])}</code></td>
                <td>{html.escape(c['case_type'])}</td>
                <td>{score}</td>
                <td>{duration}</td>
                <td>{c['tokens']:,}</td>
                <td>{html.escape(tools)}</td>
                <td class="coverage-cell">{coverage_cell}</td>
                <td><small>{html.escape(c['reason'])}</small></td>
            </tr>"""
        )

    untested_items = "".join(
        f"<li><code>{html.escape(s)}</code></li>"
        for s in coverage["untested_skills"]
    ) or "<li><em>none — every skill in plugin.json has at least one case</em></li>"

    # Shared-transcripts panel: only renders when ≥1 group of cases share
    # an agent run. Surfaces the dedup wired in TODO #1 (steps 1-3).
    shared = state.get("shared_transcripts") or []
    if shared:
        groups_html = "".join(
            f"""<div class="shared-group">
              <div class="shared-head">
                <code>{html.escape(g["transcript_id"])}</code>
                <small>· skill: <code>{html.escape(g["skill"])}</code>
                · {len(g["case_ids"])} cases</small>
              </div>
              <ul>{''.join(f'<li><code>{html.escape(cid)}</code></li>' for cid in g["case_ids"])}</ul>
            </div>"""
            for g in shared
        )
        n_cases = sum(len(g["case_ids"]) for g in shared)
        n_runs = len(shared)
        saved = n_cases - n_runs
        shared_transcripts_panel = (
            f"""<h2>Shared transcripts</h2>
<div class="panel">
  <small>{saved} agent invocation(s) saved — {n_runs} transcript(s) feeding {n_cases} cases.</small>
  {groups_html}
</div>"""
        )
    else:
        shared_transcripts_panel = ""

    completed_banner = (
        '<div class="banner done">Run complete — refresh stopped.</div>'
        if state["completed"]
        else f'<div class="banner running">Auto-refreshing every 3s · elapsed {state["elapsed_s"]:.0f}s</div>'
    )

    runner_model = state.get("runner_model", "")
    judge_model = state.get("judge_model", "")
    plugin_name = state.get("plugin_name", "")
    plugin_version = state.get("plugin_version", "")
    plugin_badge = (
        f' · plugin: <code>{html.escape(plugin_name)}@{html.escape(plugin_version)}</code>'
        if plugin_name else ""
    )
    model_badge = (
        f'<small>runner: <code>{html.escape(runner_model)}</code> · '
        f'judge: <code>{html.escape(judge_model)}</code>{plugin_badge}</small>'
        if (runner_model or judge_model)
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{refresh_meta}
<title>Behavior tests — {html.escape(state["suite_label"])}</title>
<style>
  :root {{
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #7d8590; --accent: #58a6ff;
    --pass: #3fb950; --fail: #f85149; --warn: #d29922; --running: #a371f7; --queued: #6e7681;
  }}
  body {{ font: 14px/1.5 -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }}
  h1 {{ margin: 0 0 8px 0; font-size: 18px; font-weight: 600; }}
  h2 {{ margin: 24px 0 12px 0; font-size: 14px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .banner {{ padding: 8px 12px; border-radius: 6px; margin: 12px 0; font-size: 13px; }}
  .banner.running {{ background: #1f2a44; color: var(--accent); }}
  .banner.done {{ background: #1a3a23; color: var(--pass); }}
  .grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }}
  .stat {{ background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 12px; }}
  .stat .num {{ font-size: 22px; font-weight: 600; }}
  .stat .lbl {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .stat.pass .num {{ color: var(--pass); }}
  .stat.fail .num {{ color: var(--fail); }}
  .stat.run .num {{ color: var(--running); }}
  .stat.skip .num {{ color: var(--warn); }}
  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 16px; margin-bottom: 16px; }}
  .progress {{ height: 8px; background: #21262d; border-radius: 4px; overflow: hidden; margin: 8px 0 4px; }}
  .progress > div {{ height: 100%; background: var(--accent); transition: width 0.3s; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }}
  tr.running td {{ background: rgba(163, 113, 247, 0.06); }}
  tr.failed td {{ background: rgba(248, 81, 73, 0.04); }}
  code {{ font: 12px ui-monospace, "SF Mono", monospace; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .badge.queued {{ background: var(--queued); color: white; }}
  .badge.running {{ background: var(--running); color: white; }}
  .badge.passed {{ background: var(--pass); color: black; }}
  .badge.failed {{ background: var(--fail); color: white; }}
  .badge.skipped {{ background: var(--warn); color: black; }}
  tr.skipped td {{ background: rgba(210, 153, 34, 0.04); }}
  ul {{ margin: 4px 0; padding-left: 20px; }}
  li {{ margin: 2px 0; }}
  small {{ color: var(--muted); }}
  .clock {{ font-variant-numeric: tabular-nums; }}
  details.case-details {{ margin-top: 6px; font-size: 12px; }}
  details.case-details > summary {{ color: var(--accent); cursor: pointer; user-select: none; }}
  details.case-details > summary:hover {{ text-decoration: underline; }}
  .details-body {{ padding: 8px; background: rgba(255,255,255,0.03); border-radius: 4px; margin-top: 4px; }}
  .details-body > div {{ margin: 4px 0; }}
  .coverage-cell {{ min-width: 220px; max-width: 320px; }}
  .cov-badge {{ display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .cov-badge.cov-full {{ background: var(--pass); color: black; }}
  .cov-badge.cov-partial {{ background: var(--fail); color: white; }}
  .cov-pending {{ font-size: 11px; color: var(--muted); font-style: italic; }}
  .cov-none {{ color: var(--muted); }}
  .cov-pills {{ margin-top: 4px; display: flex; flex-wrap: wrap; gap: 3px; }}
  .cov-pill {{ font-size: 11px; padding: 1px 6px; border-radius: 3px; font-family: ui-monospace, "SF Mono", monospace; }}
  .cov-pill.ok {{ background: rgba(63, 185, 80, 0.15); color: var(--pass); }}
  .cov-pill.miss {{ background: rgba(248, 81, 73, 0.15); color: var(--fail); }}
  .shared-group {{ padding: 8px 10px; border-left: 3px solid var(--accent); margin: 8px 0; background: rgba(88, 166, 255, 0.04); }}
  .shared-group .shared-head {{ font-family: ui-monospace, "SF Mono", monospace; font-size: 12px; }}
  .shared-group ul {{ margin: 4px 0 0 16px; font-size: 12px; }}
</style>
<script>
  // ─── tick the elapsed-time clocks every second ────────────────────────
  function tickClocks() {{
    const now = Date.now();
    document.querySelectorAll('.clock').forEach(el => {{
      const started = parseInt(el.dataset.started, 10);
      if (Number.isFinite(started)) {{
        const s = Math.max(0, Math.floor((now - started) / 1000));
        el.textContent = s + 's';
      }}
    }});
  }}
  setInterval(tickClocks, 1000);

  // ─── persist <details> open state across the meta-refresh ─────────────
  const OPEN_KEY = 'behavior-tests:open-details';
  function loadOpenSet() {{
    try {{ return new Set(JSON.parse(localStorage.getItem(OPEN_KEY) || '[]')); }}
    catch (e) {{ return new Set(); }}
  }}
  function saveOpenSet(set) {{
    localStorage.setItem(OPEN_KEY, JSON.stringify(Array.from(set)));
  }}
  function restoreDetails() {{
    const open = loadOpenSet();
    document.querySelectorAll('details.case-details[data-case-key]').forEach(el => {{
      const key = el.dataset.caseKey;
      if (open.has(key)) el.open = true;
      el.addEventListener('toggle', () => {{
        const set = loadOpenSet();
        if (el.open) set.add(key); else set.delete(key);
        saveOpenSet(set);
      }});
    }});
  }}

  // ─── persist scroll position across the meta-refresh ──────────────────
  setInterval(() => sessionStorage.setItem('scrollY', String(window.scrollY)), 500);
  function restoreScroll() {{
    const y = parseInt(sessionStorage.getItem('scrollY') || '0', 10);
    if (y) window.scrollTo(0, y);
  }}

  document.addEventListener('DOMContentLoaded', () => {{
    tickClocks();
    restoreDetails();
    restoreScroll();
  }});
</script>
</head>
<body>
<h1>Behavior tests · {html.escape(state["suite_label"])}</h1>
<small>started {html.escape(state["started_at"])}</small> · {model_badge}
{completed_banner}

<div class="grid">
  <div class="stat"><div class="num">{totals["planned"]}</div><div class="lbl">Planned</div></div>
  <div class="stat run"><div class="num">{totals["running"]}</div><div class="lbl">Running</div></div>
  <div class="stat pass"><div class="num">{totals["passed"]}</div><div class="lbl">Passed</div></div>
  <div class="stat fail"><div class="num">{totals["failed"]}</div><div class="lbl">Failed</div></div>
  <div class="stat skip"><div class="num">{totals.get("skipped", 0)}</div><div class="lbl">Skipped (no cache)</div></div>
  <div class="stat"><div class="num">{totals["queued"]}</div><div class="lbl">Queued</div></div>
</div>

<h2>Coverage</h2>
<div class="panel">
  <div><strong>{coverage["tested"]}</strong> of {coverage["total_skills"]} skills have at least one test case ({coverage_bar_pct}%)</div>
  <div class="progress"><div style="width: {coverage_bar_pct}%"></div></div>
  <details>
    <summary>{coverage["untested"]} untested skill(s)</summary>
    <ul>{untested_items}</ul>
  </details>
</div>

{shared_transcripts_panel}

<h2>Cases</h2>
<div class="panel">
<table>
  <thead>
    <tr><th>Status</th><th>Case ID</th><th>Skill</th><th>Type</th><th>Score</th><th>Time</th><th>Tokens</th><th>Tool calls</th><th>Expected Related Skills coverage</th><th>Reason</th></tr>
  </thead>
  <tbody>
    {''.join(case_rows) if case_rows else '<tr><td colspan="10"><em>no cases planned</em></td></tr>'}
  </tbody>
</table>
</div>

</body>
</html>"""
