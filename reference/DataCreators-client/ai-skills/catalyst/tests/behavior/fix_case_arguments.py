"""Replace TODO placeholder arguments in tests/behavior/cases/ with sensible
defaults derived from each skill's frontmatter description.

This is a one-shot follow-up to bootstrap_cases.py. Skills don't have an
`argument-hint` frontmatter field, so the bootstrap fell back to a generic
TODO. This script categorizes each skill by metadata.lifecycle-phase and
metadata.tier, then writes a default argument string that:

  - Uses ${TEST_CATALOG}.${TEST_SCHEMA} for data-discovery / profiling skills.
  - References the index data product (TEST_CONFLUENCE_PAGE_ID = the
    Index Data Product Proposal in IIKF) for document skills.
  - Stays terse — the runner expands them at runtime via Config.substitute.

Cases that already have non-TODO arguments are left untouched. Run with:

    python -m tests.behavior.fix_case_arguments [--dry-run]

Sibling of bootstrap_cases.py (the case generator this fixes up after).
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
CASES_ROOT = REPO / "tests" / "behavior" / "cases"
SKILLS_ROOT = REPO / "skills"

# Per-phase / per-skill canned arguments.  The runtime substitutes
# ${TEST_CATALOG} etc. at execution time.

DATA_DISCOVERY_SKILLS = {
    "discover-data": "Inventory tables in ${TEST_CATALOG}.${TEST_SCHEMA} that look relevant to an employee directory data product.",
    "data-profiling": "Profile tables in ${TEST_CATALOG}.${TEST_SCHEMA} for an employee directory data product. Focus on cg_employee_v4.",
    "query-catalog": "List tables in ${TEST_CATALOG}.${TEST_SCHEMA}.",
    "query-table": "Sample 20 rows from ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4 to confirm shape.",
    "profile-columns": "Profile columns of ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4.",
    "column-lineage": "Trace column lineage for cg_employee_v4 in ${TEST_CATALOG}.${TEST_SCHEMA}.",
    "data-modeling": "Produce a logical + physical model for an employee directory data product, sourced from ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4.",
    "connect-databricks": "Confirm connectivity to ${TEST_CATALOG}.${TEST_SCHEMA} and report what's reachable.",
    "marketplace-search": "Search the marketplace for an existing employee directory product before we propose a new one.",
    "load-confluence-context": "Fetch Confluence page ${TEST_CONFLUENCE_PAGE_ID} (the Index Data Product Proposal in space ${TEST_CONFLUENCE_SPACE}).",
    # fetch-confluence (capability) owns the fetch; load-confluence-context (workflow)
    # wraps it (AICAT-172). Both cases still need a concrete page argument —
    # without an explicit entry the skill falls through to the generic
    # _suggest() fallback ("Run the ... skill for an employee directory data
    # product"), which gives the agent no page to fetch and tanks the rubric
    # (AICAT-128). Point both at the same page.
    "fetch-confluence": "Fetch Confluence page ${TEST_CONFLUENCE_PAGE_ID} (the Index Data Product Proposal in space ${TEST_CONFLUENCE_SPACE}).",
}

# Phase-2 Discovery document skills — supply a short scenario describing the
# product so the document writer has a concrete subject.
PHASE2_DOCS = {
    "feasibility-report": "Assess feasibility for an employee directory data product. Sources: ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4.",
    "requirements-acceptance-criteria": "Document requirements + acceptance criteria for an employee directory data product. Hourly refresh, regulated PII.",
    "outcome-kpi-statement": "Write the outcome/KPI statement for an employee directory data product (improving HR analytics).",
    "effort-estimate": "Produce an effort estimate for the employee directory data product. Two engineers, expected scope: 6–8 weeks.",
    "business-case": "Write the business case for an employee directory data product replacing 5 fragmented HR exports.",
    "privacy-impact-assessment": "Assess privacy impact of the employee directory data product. PII includes name, manager, work location, manager_id.",
    "product-requirements-document": "Produce the PRD for an employee directory data product. Audience: HR analytics + workforce planning.",
    "demand-tracker-entry": "Log demand for an employee directory data product. Requesting team: HR Analytics.",
    "consumer-use-case-map": "Map consumers and use cases for an employee directory data product. Initial consumers: HR analytics, workforce planning, security.",
    "phase-zero-checklist": "Confirm Phase 0 readiness for a new HR Analytics data product (employee directory).",
}

# Phase-3 Design document skills.
PHASE3_DOCS = {
    "data-contract": "Draft the data contract for an employee directory data product. Source: ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4. SLAs: hourly refresh, 99.5% completeness.",
    "data-model": "Document the physical data model for an employee directory data product (single dimension table).",
    "transformation-spec": "Write the transformation spec for the employee directory product: ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4 → conformed dim_employee.",
    "architecture-diagram": "Produce an architecture diagram for an employee directory data product (Databricks medallion + Marketplace).",
    "schedule-backfill-plan": "Plan schedule + backfill for an employee directory data product. Hourly. 12-month backfill from cg_employee_v4 history.",
    "integration-blueprint": "Produce the integration blueprint for an employee directory data product (Databricks → consumers via Marketplace SQL warehouse).",
    "dataops-handoff-draft": "Draft the DataOps handoff for an employee directory data product (medallion pipeline, hourly schedule, alerts on freshness).",
    "security-design": "Produce the security design for the employee directory data product. Restricted PII; row-level security on manager hierarchy.",
}

# Phase-4..6 Build / Validate / Publish.
PHASE4_DOCS = {
    "build-checklist": "Produce a build checklist for the employee directory data product (medallion DLT pipeline).",
    "unit-test-report": "Write the unit-test report for the employee directory pipeline. 32 tests, 1 flaky test on null manager.",
    "code-review-sign-off": "Record code review sign-off for the employee directory pipeline. Reviewer: lead data engineer.",
    "source-aligned": "Generate the source-aligned pipeline for the employee directory data product. Source: ${TEST_CATALOG}.${TEST_SCHEMA}.cg_employee_v4.",
    "domain-aligned": "Generate the domain-aligned pipeline (dim_employee + fact_employee_assignment) from the source-aligned employee directory tables.",
    "consumer-aligned": "Generate the consumer-aligned views for the employee directory data product (HR analytics-shaped).",
}
PHASE5_DOCS = {
    "integration-test-report": "Write the integration test report for the employee directory pipeline. End-to-end run: source → bronze → silver → gold.",
    "data-quality-sign-off": "Record DQ sign-off for the employee directory data product. Compare measured DQ against contract thresholds.",
    "uat-sign-off": "Record UAT sign-off for the employee directory data product. UAT cohort: HR Analytics power users.",
}
PHASE6_DOCS = {
    "deployment-record": "Record the production deployment of the employee directory data product. Environment: prod. Rollback: redeploy v1.0.",
    "consumer-onboarding-guide": "Write the consumer onboarding guide for the employee directory data product (Marketplace → SQL warehouse).",
    "release-notes": "Write release notes for v1.0 of the employee directory data product.",
}

# Phase-7..8 Sustain.
PHASE7_DOCS = {
    "runbook": "Write the runbook for the employee directory data product. Hourly DLT pipeline; alert if freshness > 90 minutes.",
    "incident-log": "Log a sample incident for the employee directory data product (hourly refresh missed at 02:00 UTC).",
    "sla-dashboard-spec": "Produce the SLA dashboard spec for the employee directory data product (freshness, completeness, error rate).",
    "warranty-handoff-sign-off": "Record warranty handoff sign-off for the employee directory data product (build team → ops).",
    "usage-analytics-report": "Write the usage analytics report for the employee directory data product (monthly summary).",
    "downstream-impact-assessment": "Assess downstream impact of changing the manager_id column in the employee directory data product.",
    "deprecation-notice": "Draft the deprecation notice for the legacy employee_export_v3 table, replaced by the employee directory data product.",
}

# Misc / cross-cutting.
MISC = {
    "poc-spike-findings": "Document POC spike findings for the employee directory data product. Spike: validating row-level security on manager hierarchy.",
    "nfr-specification": "Write the NFR specification for the employee directory data product. Hourly refresh, p99 query < 2s, 99.9% availability.",
}

ALL_TABLES: dict[str, str] = {
    **DATA_DISCOVERY_SKILLS,
    **PHASE2_DOCS,
    **PHASE3_DOCS,
    **PHASE4_DOCS,
    **PHASE5_DOCS,
    **PHASE6_DOCS,
    **PHASE7_DOCS,
    **MISC,
}


def _parse_skill_name(case_path: Path) -> str:
    return case_path.parent.name


def _suggest(skill_name: str, description: str) -> str:
    """Return a sensible default argument for this skill, falling back to a
    generic instruction if no entry exists in ALL_TABLES."""
    if skill_name in ALL_TABLES:
        return ALL_TABLES[skill_name]
    # Last-resort fallback: derive from description.
    desc_short = re.sub(r"\s+", " ", description).strip()[:200]
    return f"Run the {skill_name} skill for an employee directory data product. {desc_short}"


def _read_skill_description(skill_name: str) -> str:
    skill_md = SKILLS_ROOT / skill_name / "SKILL.md"
    if not skill_md.exists():
        return ""
    text = skill_md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return ""
    fm = yaml.safe_load(m.group(1)) or {}
    return (fm.get("description") or "").strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    updated, untouched = 0, 0
    for case_yaml in sorted(CASES_ROOT.rglob("case-01*.yaml")):
        data = yaml.safe_load(case_yaml.read_text())
        if not isinstance(data, dict):
            continue
        if data.get("type") != "artifact":
            continue
        current = ((data.get("input") or {}).get("arguments") or "")
        if "TODO" not in current:
            untouched += 1
            continue
        skill_name = _parse_skill_name(case_yaml)
        description = _read_skill_description(skill_name)
        new_args = _suggest(skill_name, description)
        data.setdefault("input", {})["arguments"] = new_args
        if args.dry_run:
            print(f"[dry-run] {case_yaml.relative_to(REPO)} -> {new_args[:80]}...")
        else:
            case_yaml.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False, width=100))
            print(f"updated  {case_yaml.relative_to(REPO)}")
        updated += 1

    print(f"\nUpdated: {updated} · Untouched: {untouched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
