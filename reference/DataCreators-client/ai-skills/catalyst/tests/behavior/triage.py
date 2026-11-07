"""Behavior-test triage report generator.

Reads cached behavior-test results from workspace/behavior-tests and emits
structured JSON for downstream automation.
"""

from __future__ import annotations

import re
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Single source of truth for failure taxonomy.
# Order matters for _classify_failure: harness first (catches runtime noise
# before content checks), then structural checks, then quality/format.
FAILURE_TAXONOMY: dict[str, tuple[str, str]] = {
    "orchestrator-delegation": ("high",   "Orchestrator behavior did not delegate to expected sub-skills."),
    "template-conformance":    ("medium", "Output structure did not conform to the expected template."),
    "shared-code":             ("medium", "Skill did not use the expected shared component path."),
    "quick-fix":               ("low",    "Failure indicates a localized content or formatting fix."),
    "harness":                 ("high",   "Failure appears to be test harness/runtime related."),
}
FAILURE_TYPES = tuple(FAILURE_TAXONOMY)
SEVERITY_BY_TYPE = {k: v[0] for k, v in FAILURE_TAXONOMY.items()}
SUMMARY_BY_TYPE  = {k: v[1] for k, v in FAILURE_TAXONOMY.items()}


def _classify_failure(reason: str) -> str:
    text = (reason or "").lower()

    if any(k in text for k in ("runner error", "cache miss", "max_turns", "max_budget", "timeout", "connectionerror")):
        return "harness"
    if any(k in text for k in ("missing expected sub-skills", "unexpected sub-skills", "self-invocation")):
        return "orchestrator-delegation"
    if any(k in text for k in ("matches_template", "template", "missing required headings")):
        return "template-conformance"
    if any(k in text for k in ("uses_components", "component coverage", "expected component")):
        return "shared-code"
    if any(k in text for k in ("no_placeholder_text", "placeholder", "weighted")):
        return "quick-fix"

    # Unknown reason — fail loud so novel failures aren't silently downgraded.
    return "harness"


def _skill_name(skill_path: str) -> str:
    if not skill_path:
        return "unknown"
    return skill_path.rstrip("/").rsplit("/", 1)[-1] or "unknown"


def _build_case_path_index(cases_root: Path, repo_root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for yaml_path in cases_root.rglob("*.yaml"):
        try:
            payload = yaml.safe_load(yaml_path.read_text())
        except (yaml.YAMLError, OSError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            try:
                index[payload["id"]] = yaml_path.relative_to(repo_root).as_posix()
            except ValueError:
                index[payload["id"]] = yaml_path.as_posix()
    return index


def _lookup_gh_issues(case_ids: list[str], repo_root: Path) -> dict[str, int]:
    if not case_ids:
        return {}

    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--limit",
                "1000",
                "--state",
                "all",
                "--json",
                "number,title",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {}

    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

    mapping: dict[str, int] = {}
    deduped = [c for c in dict.fromkeys(case_ids) if c]  # unique, non-empty
    for issue in issues:
        title = str(issue.get("title", ""))
        number = issue.get("number")
        if not isinstance(number, int):
            continue
        for case_id in deduped:
            # Regex match against issues.py title format: "] {case_id}" at a
            # word boundary. Anchoring prevents case-01 matching case-010.
            if re.search(rf"\]\s+{re.escape(case_id)}(?:\s|$)", title) \
                    and case_id not in mapping:
                mapping[case_id] = number
    return mapping


def build_triage_report(
    *,
    workspace_dir: Path,
    cases_root: Path,
    repo_root: Path,
    runtime_version: str,
    lookup_gh_issues: bool,
) -> dict[str, Any]:
    status_path = workspace_dir / "live-report" / "status.json"
    cache_dir = workspace_dir / "cache"

    if not status_path.exists():
        raise RuntimeError(
            f"No cached results found: missing {status_path}. Run `bin/bt full` or `bin/bt execute` first."
        )

    if not any(cache_dir.glob("*__with_skill.json")) and not any(cache_dir.glob("*__without_skill.json")):
        raise RuntimeError(
            f"No cached results found in {cache_dir}. Run `bin/bt full` or `bin/bt execute` first."
        )

    state = json.loads(status_path.read_text())
    cases = state.get("cases") or []
    failed_cases = [c for c in cases if c.get("status") == "failed"]

    case_path_index = _build_case_path_index(cases_root=cases_root, repo_root=repo_root)
    case_ids = [str(c.get("case_id", "")) for c in failed_cases]
    gh_issue_by_case: dict[str, int] = {}
    if lookup_gh_issues:
        gh_issue_by_case = _lookup_gh_issues(case_ids=case_ids, repo_root=repo_root)

    findings: list[dict[str, Any]] = []
    counts = {t: 0 for t in FAILURE_TYPES}

    for case in failed_cases:
        case_id = str(case.get("case_id", "unknown"))
        reason = str(case.get("reason") or "")
        failure_type = _classify_failure(reason)
        counts[failure_type] += 1

        findings.append(
            {
                "skill_name": _skill_name(str(case.get("skill", ""))),
                "case_id": case_id,
                "failure_type": failure_type,
                "severity": SEVERITY_BY_TYPE[failure_type],
                "summary": SUMMARY_BY_TYPE[failure_type],
                "gh_issue": gh_issue_by_case.get(case_id),
                "test_path": case_path_index.get(case_id, "unknown"),
                "reason": reason,
            }
        )

    return {
        "runtime_version": runtime_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_dir": workspace_dir.as_posix(),
        "summary": {
            "total_cases": len(cases),
            "failed_cases": len(failed_cases),
            "findings": len(findings),
            "by_failure_type": counts,
        },
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tests.behavior.triage")
    parser.add_argument(
        "--version",
        default="unknown",
        help="Runtime version label to include in triage output (for example ai-catalyst-1.5.0).",
    )
    parser.add_argument(
        "--workspace-dir",
        default="workspace/behavior-tests",
        help="Behavior test workspace directory containing cache/ and live-report/status.json.",
    )
    parser.add_argument(
        "--cases-root",
        default="tests/behavior/cases",
        help="Root directory containing behavior case YAML files.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Defaults to <workspace-dir>/triage-report.json.",
    )
    parser.add_argument(
        "--lookup-gh-issues",
        action="store_true",
        help="Best-effort lookup of GitHub issue numbers for each case_id by searching issue titles.",
    )

    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    workspace_dir = Path(args.workspace_dir)
    cases_root = Path(args.cases_root)
    output_path = Path(args.output) if args.output else (workspace_dir / "triage-report.json")

    try:
        report = build_triage_report(
            workspace_dir=workspace_dir,
            cases_root=cases_root,
            repo_root=repo_root,
            runtime_version=args.version,
            lookup_gh_issues=args.lookup_gh_issues,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
