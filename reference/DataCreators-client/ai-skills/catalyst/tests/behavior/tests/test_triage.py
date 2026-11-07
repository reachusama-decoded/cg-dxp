import json
import os
from pathlib import Path

from tests.behavior import triage


def _write_case_yaml(cases_root: Path, case_id: str, skill: str) -> None:
    parts = case_id.split(".")
    skill_dir = cases_root / skill
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / f"{parts[-1]}.yaml").write_text(
        "\n".join(
            [
                f"id: {case_id}",
                f"skill: skills/{skill}",
                "type: artifact",
                "input:",
                '  arguments: ""',
            ]
        )
        + "\n"
    )


def _write_workspace_state(workspace_dir: Path, cases: list[dict]) -> None:
    (workspace_dir / "live-report").mkdir(parents=True, exist_ok=True)
    (workspace_dir / "cache").mkdir(parents=True, exist_ok=True)

    status = {
        "cases": cases,
        "totals": {
            "planned": len(cases),
            "failed": sum(1 for c in cases if c.get("status") == "failed"),
            "passed": sum(1 for c in cases if c.get("status") == "passed"),
        },
    }
    (workspace_dir / "live-report" / "status.json").write_text(json.dumps(status, indent=2))

    for case in cases:
        transcript_id = case.get("transcript_id")
        if not transcript_id:
            continue
        (workspace_dir / "cache" / f"{transcript_id}__with_skill.json").write_text("{}")


def test_build_triage_report_categorizes_all_failure_types(tmp_path: Path):
    repo_root = tmp_path
    cases_root = repo_root / "tests" / "behavior" / "cases"
    workspace_dir = repo_root / "workspace" / "behavior-tests"

    cases = [
        {
            "case_id": "discover-data.case-01",
            "skill": "skills/discover-data",
            "status": "failed",
            "reason": "missing expected sub-skills: data-profiling",
            "transcript_id": "discover-data__a1b2c3d4",
        },
        {
            "case_id": "feasibility-report.case-01",
            "skill": "skills/feasibility-report",
            "status": "failed",
            "reason": "matches_template failed: missing required headings",
            "transcript_id": "feasibility-report__a1b2c3d4",
        },
        {
            "case_id": "source-aligned.case-01",
            "skill": "skills/source-aligned",
            "status": "failed",
            "reason": "uses_components check failed",
            "transcript_id": "source-aligned__a1b2c3d4",
        },
        {
            "case_id": "release-notes.case-01",
            "skill": "skills/release-notes",
            "status": "failed",
            "reason": "no_placeholder_text failed",
            "transcript_id": "release-notes__a1b2c3d4",
        },
        {
            "case_id": "dplc-design.case-01",
            "skill": "skills/dplc-design",
            "status": "failed",
            "reason": "runner error: RuntimeError: transport reset",
            "transcript_id": "dplc-design__a1b2c3d4",
        },
        {
            "case_id": "data-profiling.case-01",
            "skill": "skills/data-profiling",
            "status": "passed",
            "reason": "",
            "transcript_id": "data-profiling__a1b2c3d4",
        },
    ]

    for case in cases:
        _write_case_yaml(cases_root=cases_root, case_id=case["case_id"], skill=case["skill"].split("/")[-1])

    _write_workspace_state(workspace_dir=workspace_dir, cases=cases)

    report = triage.build_triage_report(
        workspace_dir=workspace_dir,
        cases_root=cases_root,
        repo_root=repo_root,
        runtime_version="ai-catalyst-1.5.0",
        lookup_gh_issues=False,
    )

    assert report["runtime_version"] == "ai-catalyst-1.5.0"
    assert report["summary"]["total_cases"] == 6
    assert report["summary"]["failed_cases"] == 5
    assert report["summary"]["findings"] == 5
    assert report["summary"]["by_failure_type"]["orchestrator-delegation"] == 1
    assert report["summary"]["by_failure_type"]["template-conformance"] == 1
    assert report["summary"]["by_failure_type"]["shared-code"] == 1
    assert report["summary"]["by_failure_type"]["quick-fix"] == 1
    assert report["summary"]["by_failure_type"]["harness"] == 1

    for finding in report["findings"]:
        assert "skill_name" in finding
        assert "case_id" in finding
        assert "failure_type" in finding
        assert "severity" in finding
        assert "summary" in finding
        assert "gh_issue" in finding
        assert "test_path" in finding
        assert finding["test_path"].startswith("tests/behavior/cases/")


def test_main_writes_output_file_and_stdout_json(tmp_path: Path, capsys):
    repo_root = tmp_path
    cases_root = repo_root / "tests" / "behavior" / "cases"
    workspace_dir = repo_root / "workspace" / "behavior-tests"

    case = {
        "case_id": "discover-data.case-01",
        "skill": "skills/discover-data",
        "status": "failed",
        "reason": "missing expected sub-skills",
        "transcript_id": "discover-data__a1b2c3d4",
    }

    _write_case_yaml(cases_root=cases_root, case_id=case["case_id"], skill="discover-data")
    _write_workspace_state(workspace_dir=workspace_dir, cases=[case])

    output_path = workspace_dir / "triage-report.json"

    old_cwd = Path.cwd()
    try:
        # The CLI uses cwd as repo root for relative paths.
        os.chdir(repo_root)
        rc = triage.main([
            "--version",
            "ai-catalyst-1.5.0",
            "--workspace-dir",
            str(workspace_dir),
            "--cases-root",
            str(cases_root),
            "--output",
            str(output_path),
        ])
    finally:
        os.chdir(old_cwd)

    assert rc == 0
    assert output_path.exists()

    payload = json.loads(output_path.read_text())
    assert payload["runtime_version"] == "ai-catalyst-1.5.0"

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["summary"]["failed_cases"] == 1


def test_main_returns_1_when_cache_missing(tmp_path: Path, capsys):
    repo_root = tmp_path
    workspace_dir = repo_root / "workspace" / "behavior-tests"
    cases_root = repo_root / "tests" / "behavior" / "cases"

    (workspace_dir / "live-report").mkdir(parents=True, exist_ok=True)
    (workspace_dir / "live-report" / "status.json").write_text('{"cases": []}')

    old_cwd = Path.cwd()
    try:
        os.chdir(repo_root)
        rc = triage.main([
            "--workspace-dir",
            str(workspace_dir),
            "--cases-root",
            str(cases_root),
        ])
    finally:
        os.chdir(old_cwd)

    assert rc == 1
    stderr = capsys.readouterr().err
    assert "No cached results found" in stderr


def test_gh_issue_lookup_title_format_contract():
    """Pin the title-format contract between issues.py and triage.py.

    issues.py produces titles like:
      "[behavior-test FAIL] discover-data.case-01 — reason text"
      "[behavior-test PASS] discover-data.case-01 — case review..."

    triage._lookup_gh_issues must match those titles correctly and NOT
    match a similar but distinct case ID (e.g. case-010 when looking for case-01).
    """
    from tests.behavior.triage import _lookup_gh_issues
    from pathlib import Path
    from unittest.mock import patch
    import json

    issues = [
        {"number": 10, "title": "[behavior-test FAIL] discover-data.case-01 — missing sub-skills"},
        {"number": 11, "title": "[behavior-test FAIL] discover-data.case-010 — weighted"},
        {"number": 12, "title": "[behavior-test PASS] feasibility-report.case-01 — case review"},
    ]

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = json.dumps(issues)
        mock_run.return_value.returncode = 0

        result = _lookup_gh_issues(
            case_ids=["discover-data.case-01", "feasibility-report.case-01"],
            repo_root=Path("."),
        )

    # case-01 should match issue 10, NOT issue 11 (case-010)
    assert result["discover-data.case-01"] == 10
    assert result["feasibility-report.case-01"] == 12
    # case-010 was not requested, should not appear
    assert 11 not in result.values()
