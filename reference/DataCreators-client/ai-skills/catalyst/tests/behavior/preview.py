"""Render the live-report dashboard from synthetic outcomes.

For visually verifying changes to live_report.py without burning a real
agent + judge run. Three cases exercise the column shapes:
  - behavior case with expected_sequence + expected_components
  - artifact case with expected_components
  - artifact case with no expected_components ("—" cell)

Run via `bin/bt preview` and open the printed file:// URL.
"""
from __future__ import annotations
from pathlib import Path

from tests.behavior.cases import ArtifactCase, BehaviorCase, Criterion, Input, Rubric
from tests.behavior.config import Config
from tests.behavior.live_report import LiveReport
from tests.behavior.report import CaseOutcome


def main(out_dir: Path = Path("/tmp/live-report-preview")) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        BehaviorCase(
            id="dplc-discovery.case-01-behavior",
            skill="skills/dplc-discovery", type="behavior",
            description="Phase 2 orchestrator must invoke discover-data, data-profiling, feasibility-report.",
            input=Input(arguments="employee headcount product"),
            expected_sequence=[
                "skills/discover-data", "skills/data-profiling", "skills/feasibility-report",
            ],
            expected_components=["skills/core/discover.py"],
        ),
        ArtifactCase(
            id="discover-data.case-01-happy-path",
            skill="skills/discover-data", type="artifact",
            description="Discover tables related to employees.",
            input=Input(arguments="${TEST_CATALOG} employee headcount"),
            rubric=Rubric(threshold=0.75, criteria=[Criterion(id="x", weight=1.0, prompt="?")]),
            expected_components=["skills/core/discover.py", "skills/clients/databricks.py"],
        ),
        ArtifactCase(
            id="business-case.case-01-happy-path",
            skill="skills/business-case", type="artifact",
            description="Generate a business case (no expected components).",
            input=Input(arguments="employee directory"),
            rubric=Rubric(threshold=0.75, criteria=[Criterion(id="x", weight=1.0, prompt="?")]),
        ),
    ]

    lr = LiveReport(
        output_dir=out_dir, cases=cases,
        all_skills=[
            "skills/dplc-discovery", "skills/discover-data",
            "skills/business-case", "skills/missing-skill",
        ],
        config=Config.from_env(),
        suite_label="preview",
        runner_model="databricks-claude-sonnet-4-6",
        judge_model="databricks-claude-haiku-4-5",
    )

    lr.start_case("dplc-discovery.case-01-behavior")
    lr.finish_case("dplc-discovery.case-01-behavior", CaseOutcome(
        case_id="dplc-discovery.case-01-behavior", passed=False,
        reason="missing expected sub-skills: ['skills/feasibility-report']",
        weighted_score=None, duration_s=183.4,
        input_tokens=12000, output_tokens=2400,
        tool_call_counts={"Bash": 4, "Read": 6, "Skill": 2},
        sub_skills=["discover-data", "data-profiling"],
        component_coverage=[{"component": "skills/core/discover.py", "matched": True}],
    ))

    lr.start_case("discover-data.case-01-happy-path")
    lr.finish_case("discover-data.case-01-happy-path", CaseOutcome(
        case_id="discover-data.case-01-happy-path", passed=False,
        reason="uses_components: agent did not invoke expected components",
        weighted_score=None, duration_s=241.8,
        input_tokens=9000, output_tokens=8000,
        tool_call_counts={"Bash": 5, "Glob": 3},
        component_coverage=[
            {"component": "skills/core/discover.py", "matched": True},
            {"component": "skills/clients/databricks.py", "matched": False},
        ],
    ))

    lr.start_case("business-case.case-01-happy-path")
    lr.finish_case("business-case.case-01-happy-path", CaseOutcome(
        case_id="business-case.case-01-happy-path", passed=True,
        reason="", weighted_score=0.84, duration_s=152.1,
        input_tokens=5000, output_tokens=3500,
        tool_call_counts={"Bash": 2, "Read": 4},
    ))
    lr.close()
    print(f"Open: file://{out_dir.resolve()}/index.html")


if __name__ == "__main__":
    main()
