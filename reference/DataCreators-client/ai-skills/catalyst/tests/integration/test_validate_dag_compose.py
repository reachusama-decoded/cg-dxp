"""Compose-contract integration test for /validate-dag.

The /validate-dag skill is the read-only auditor counterpart to
/generate-dag. It mirrors the producer's RFD 0011 rule set, applies it
to existing DAGs, and emits a Markdown compliance report with a
grep-able `VERDICT:` line.

This is structurally a cross-skill + cross-file contract test, not a
unit test. It does NOT exercise the LLM (the bt harness has no
setup.files: support yet — see OQ-7 in the design spec). Instead, it
asserts the skill's load-bearing contracts are documented in the skill
content itself:

- SKILL.md declares the read-only tool surface (no Bash)
- SKILL.md cites /generate-dag and documents the VERDICT grep contract
- references/checks-by-section.md enumerates detection rules per
  directive, with the recent reviewer-driven precisions on
  execution_timeout shapes and DBX-DAB-003's email two-step detector
- references/findings-severity.md states the verdict-computation rule
  (blocker_count > 0 → NON_COMPLIANT) and the mode-aware downgrade
  matrix
- references/pattern-detection.md documents Glob-based (not Bash)
  discovery
- templates/compliance-report.md renders the exact VERDICT line spec

If any of these structural anchors drifts, the agent will silently
freelance the audit and emit reports that don't match the spec — or
worse, fail the read-only invariant. This test catches that before
the skill ships into a team's repo.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_DAG_DIR = REPO_ROOT / "skills" / "validate-dag"
SKILL_MD = VALIDATE_DAG_DIR / "SKILL.md"
PATTERN_DETECTION = VALIDATE_DAG_DIR / "references" / "pattern-detection.md"
CHECKS_BY_SECTION = VALIDATE_DAG_DIR / "references" / "checks-by-section.md"
FINDINGS_SEVERITY = VALIDATE_DAG_DIR / "references" / "findings-severity.md"
REPORT_TEMPLATE = VALIDATE_DAG_DIR / "templates" / "compliance-report.md"

# Sibling skill the validator cites (but does NOT depend on running)
GENERATE_DAG_SKILL_MD = REPO_ROOT / "skills" / "generate-dag" / "SKILL.md"
RFD_0011_CITATIONS = REPO_ROOT / "skills" / "generate-dag" / "references" / "rfd-0011-citations.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL_MD.exists(), f"SKILL.md missing: {SKILL_MD}"
    return SKILL_MD.read_text()


@pytest.fixture(scope="module")
def pattern_detection_text() -> str:
    assert PATTERN_DETECTION.exists(), f"pattern-detection.md missing: {PATTERN_DETECTION}"
    return PATTERN_DETECTION.read_text()


@pytest.fixture(scope="module")
def checks_text() -> str:
    assert CHECKS_BY_SECTION.exists(), f"checks-by-section.md missing: {CHECKS_BY_SECTION}"
    return CHECKS_BY_SECTION.read_text()


@pytest.fixture(scope="module")
def severity_text() -> str:
    assert FINDINGS_SEVERITY.exists(), f"findings-severity.md missing: {FINDINGS_SEVERITY}"
    return FINDINGS_SEVERITY.read_text()


@pytest.fixture(scope="module")
def template_text() -> str:
    assert REPORT_TEMPLATE.exists(), f"compliance-report.md missing: {REPORT_TEMPLATE}"
    return REPORT_TEMPLATE.read_text()


# ---------------------------------------------------------------------------
# Read-only tool surface — the invariant that everything else rests on
# ---------------------------------------------------------------------------

class TestReadOnlyToolSurface:
    """`/validate-dag`'s read-only claim must be enforceable by the tool surface."""

    def test_allowed_tools_does_not_include_bash(self, skill_text):
        # Tool surface declared in frontmatter. Bash would let a future
        # maintainer shell out and write side-effect files; the read-only
        # invariant must rest on the surface, not on prompt discipline.
        match = re.search(r"^allowed-tools:\s*(.+)$", skill_text, re.MULTILINE)
        assert match, "SKILL.md frontmatter must declare allowed-tools"
        tools = match.group(1)
        assert "Bash" not in tools, (
            f"allowed-tools must NOT include Bash (read-only invariant); got: {tools}"
        )

    def test_pattern_detection_uses_glob_not_shell(self, pattern_detection_text):
        # Discovery section should be Glob-based, not bash commands.
        assert "Glob:" in pattern_detection_text, (
            "pattern-detection.md discovery section must use Glob: patterns"
        )
        assert "```bash" not in pattern_detection_text, (
            "pattern-detection.md must NOT include bash command blocks (read-only invariant)"
        )


# ---------------------------------------------------------------------------
# SKILL.md core contracts
# ---------------------------------------------------------------------------

class TestSkillMdContracts:
    """Load-bearing contracts the agent must see in SKILL.md."""

    def test_cites_generate_dag_not_depends_on(self, skill_text):
        # The validator does not require /generate-dag to have run; it
        # only cites its references in remediation hints.
        assert "cites:" in skill_text, (
            "SKILL.md frontmatter must use `cites:` (not `dependencies:`) for /generate-dag"
        )
        # And explicitly NOT in a dependencies block
        frontmatter = skill_text.split("---", 2)[1] if skill_text.startswith("---") else ""
        deps_block = re.search(r"^\s*dependencies:\s*\n((?:\s+-\s+.+\n)+)", frontmatter, re.MULTILINE)
        if deps_block:
            assert "generate-dag" not in deps_block.group(1), (
                "/generate-dag must not appear under `dependencies:` — use `cites:`"
            )

    def test_provisional_caveat_for_discussion_state_rules(self, skill_text):
        # The auditor enforces 016-022 + DBX-DAB-001/-003 which are not
        # yet ratified in RFD 0011. The provisional caveat is what keeps
        # the anti-goal at "No new rules" from contradicting the standards
        # list.
        assert re.search(r"provisional|discussion-state", skill_text, re.IGNORECASE), (
            "SKILL.md must carry the provisional-rules caveat for 016-022 + DBX-DAB-001/-003"
        )

    def test_modes_documented(self, skill_text):
        """All three modes must be spelled out, with production as default."""
        for mode in ("production", "prototype", "lift-and-shift"):
            assert mode in skill_text, f"SKILL.md must document `{mode}` mode"

    def test_verdict_grep_contract_documented(self, skill_text):
        """The VERDICT line shape must be specified verbatim for CI grep."""
        # The contract: VERDICT: <COMPLIANT|NON_COMPLIANT> — <N> blocker, ...
        # Look for any contiguous chunk that has all the required tokens.
        verdict_pattern = re.search(
            r"VERDICT:.+COMPLIANT.+NON_COMPLIANT.+blocker.+advisory.+ok.+n-a",
            skill_text,
            re.DOTALL,
        )
        assert verdict_pattern, (
            "SKILL.md must document the exact VERDICT line shape including all four count tokens"
        )

    def test_read_only_anti_goal_present(self, skill_text):
        """The read-only invariant must be stated as an anti-goal."""
        # The anti-goal section explicitly says the validator never modifies files.
        anti_goal_match = re.search(
            r"(?:never modifies?|read-only|no auto-fix)",
            skill_text,
            re.IGNORECASE,
        )
        assert anti_goal_match, "SKILL.md must state the read-only invariant"

    def test_routes_to_generate_dag_lift_and_shift_for_fixes(self, skill_text):
        """Users wanting fixes must be routed to /generate-dag lift-and-shift."""
        assert re.search(r"lift-and-shift", skill_text), (
            "SKILL.md must route remediation requests to /generate-dag lift-and-shift mode"
        )

    def test_inline_mode_documented(self, skill_text):
        """The skill must explicitly accept inline carrier content in the prompt.

        Found via bt full-suite run: when invoked via the bt harness (which
        has no setup.files: support), the LLM defaulted to reading an
        e2e fixture from disk instead of auditing the inlined DAG in
        arguments. The fix is to declare inline mode as a first-class input
        and gate disk discovery on disk-mode.
        """
        # Look for inline-mode language in the Inputs section.
        assert "Inline carrier content" in skill_text or "inline content" in skill_text.lower(), (
            "SKILL.md must declare inline-content as a first-class input mode"
        )
        # And the priority order — inline wins over path references.
        assert "inline wins" in skill_text.lower() or "inline mode" in skill_text.lower(), (
            "SKILL.md must document the inline-vs-disk priority order"
        )

    def test_inline_mode_gates_disk_discovery(self, skill_text):
        """Steps 1, 2, and 4 must explicitly branch on inline vs disk mode.

        Without explicit branches, the LLM defaults to disk discovery and
        ignores the inline content (the failure observed in the bt suite).
        """
        # Step 2 must call out that companion-artifact lookup is skipped in
        # inline mode (or equivalent).
        assert re.search(
            r"inline mode.*(?:skip|not provided|n-a)",
            skill_text,
            re.IGNORECASE | re.DOTALL,
        ), (
            "SKILL.md Step 2 must explicitly skip disk companion-artifact lookups in inline mode"
        )
        # Step 4 must call out that DBX-DAB-001 is n-a in inline mode.
        assert "bundle not provided in inline mode" in skill_text or re.search(
            r"DBX-DAB-001.*inline mode",
            skill_text,
            re.IGNORECASE | re.DOTALL,
        ), (
            "SKILL.md Step 4 must explicitly emit n-a for DBX-DAB-001 in inline mode"
        )


# ---------------------------------------------------------------------------
# checks-by-section.md — per-directive detection contracts
# ---------------------------------------------------------------------------

class TestChecksBySectionContracts:
    """The per-directive detection map must enumerate every rule the spec claims."""

    REQUIRED_RULE_IDS = [
        # §1 idempotency
        "PY-AIRFLOW-001",
        # §2 retries
        "PY-AIRFLOW-003",
        "PY-AIRFLOW-004",
        "PY-AIRFLOW-016",
        # §3 deferrability
        "PY-AIRFLOW-017",
        # §4 resourcing
        "PY-AIRFLOW-005",
        "PY-AIRFLOW-018",
        # §5 scheduling
        "PY-AIRFLOW-002",
        "PY-AIRFLOW-006",
        "PY-AIRFLOW-019",
        "PY-AIRFLOW-015",
        # §6 observability
        "PY-AIRFLOW-007",
        "PY-AIRFLOW-008",
        # §7 task design
        "PY-AIRFLOW-009",
        "PY-AIRFLOW-010",
        "PY-AIRFLOW-011",
        # §8 code org
        "PY-AIRFLOW-012",
        # §9 secrets
        "PY-AIRFLOW-013",
        "PY-AIRFLOW-020",
        # §10 testing
        "PY-AIRFLOW-014",
        "PY-AIRFLOW-021",
        "PY-AIRFLOW-022",
        # Bundle compose
        "DBX-DAB-001",
        "DBX-DAB-003",
    ]

    def test_every_required_rule_has_a_detection_entry(self, checks_text):
        missing = [rid for rid in self.REQUIRED_RULE_IDS if rid not in checks_text]
        assert not missing, (
            f"checks-by-section.md is missing detection entries for: {missing}"
        )

    def test_comment_aware_grep_rule_documented(self, checks_text):
        """Pedagogical comments (e.g. `# do not emit datetime.now()`) must not false-positive."""
        assert "comment-aware grep" in checks_text.lower() or "comment-only" in checks_text.lower(), (
            "checks-by-section.md must document the comment-aware grep rule to prevent false positives"
        )

    def test_execution_timeout_accepts_multiple_shapes(self, checks_text):
        """PY-AIRFLOW-017 execution_timeout must accept mapping, *_seconds/_minutes/_hours, or timedelta."""
        # The reviewer flagged the original spec for being too strict;
        # the fixture and behavior cases use varied shapes that must all
        # be accepted.
        assert "execution_timeout_minutes" in checks_text, (
            "PY-AIRFLOW-017 must enumerate execution_timeout_minutes as an accepted shape"
        )
        assert "execution_timeout_seconds" in checks_text or "execution_timeout_hours" in checks_text, (
            "PY-AIRFLOW-017 must enumerate _seconds/_hours forms"
        )

    def test_email_detector_does_not_false_positive_on_contact_info(self, checks_text):
        """DBX-DAB-003 must not flag legitimate `default_args.email` + `email_on_failure: false`."""
        # Look for the two-step detection language: opt-in via *_on_failure: true OR
        # email: present + email_on_failure unset.
        dab_003 = re.search(
            r"DBX-DAB-003.*?(?=\n##\s|\Z)",
            checks_text,
            re.DOTALL,
        )
        assert dab_003, "DBX-DAB-003 entry must exist"
        body = dab_003.group(0)
        assert re.search(r"email_on_failure.*[Tt]rue", body), (
            "DBX-DAB-003 must explicitly require email_on_failure: true (or equivalent) before flagging"
        )

    def test_required_mds_tag_set_is_five_keys(self, checks_text):
        """PY-AIRFLOW-007 must enumerate all 5 required MDS tag keys."""
        py_007 = re.search(
            r"PY-AIRFLOW-007.*?(?=\n>\s*\*\*PY-AIRFLOW-008|\n##\s|\Z)",
            checks_text,
            re.DOTALL,
        )
        assert py_007, "PY-AIRFLOW-007 entry must exist"
        body = py_007.group(0)
        for key in ("l1_domain", "l1_xmatters_group", "lifecycle_phase",
                    "data_classification", "criticality"):
            assert key in body, f"PY-AIRFLOW-007 must enumerate `{key}` as a required tag"


# ---------------------------------------------------------------------------
# findings-severity.md — verdict computation + mode matrix
# ---------------------------------------------------------------------------

class TestFindingsSeverity:
    """The severity model must specify verdict computation and the mode matrix."""

    def test_four_severity_levels_defined(self, severity_text):
        for sev in ("blocker", "advisory", "ok", "n-a"):
            assert sev in severity_text.lower(), (
                f"findings-severity.md must define the `{sev}` severity level"
            )

    def test_verdict_computation_rule(self, severity_text):
        """Verdict must be NON_COMPLIANT iff any blocker — never advisory/n-a-driven."""
        # The doctrine is stated explicitly.
        assert re.search(
            r"blocker.{0,80}NON_COMPLIANT|NON_COMPLIANT.{0,80}blocker",
            severity_text,
            re.IGNORECASE | re.DOTALL,
        ), "findings-severity.md must document the verdict-computation rule"

    def test_mode_matrix_present(self, severity_text):
        """Mode-aware downgrade matrix must enumerate prototype + lift-and-shift downgrades."""
        for mode in ("production", "prototype", "lift-and-shift"):
            assert mode in severity_text, f"mode matrix must list `{mode}`"

    def test_prototype_downgrades_match_skill_modes_table(self, severity_text, skill_text):
        """The prototype downgrade set must agree across SKILL.md and findings-severity.md.

        The reviewer caught a divergence here in an earlier round (SKILL.md
        downgraded 3 rules; findings-severity.md downgraded 6). Keep them
        in lock-step.
        """
        # Both files should mention the same rule clusters in prototype mode.
        # We check that PY-AIRFLOW-007, -008, -017, -018, -012, -014, -022 all
        # appear in both files (these are the canonical prototype downgrades).
        for rule in ("PY-AIRFLOW-007", "PY-AIRFLOW-008", "PY-AIRFLOW-017",
                     "PY-AIRFLOW-018", "PY-AIRFLOW-012"):
            assert rule in severity_text, f"findings-severity.md must reference `{rule}`"
            assert rule in skill_text, f"SKILL.md must reference `{rule}`"


# ---------------------------------------------------------------------------
# Template — the exact VERDICT line CI greps for
# ---------------------------------------------------------------------------

class TestComplianceReportTemplate:
    """The Markdown report template must render the grep-able VERDICT line verbatim."""

    def test_verdict_line_exact_shape(self, template_text):
        # The single line CI grepss for. Order, separators, and tokens
        # must all be present.
        verdict_line = re.search(
            r"VERDICT:\s*\{\{\s*VERDICT\s*\}\}\s*—\s*"
            r"\{\{\s*BLOCKER_COUNT\s*\}\}\s*blocker,\s*"
            r"\{\{\s*ADVISORY_COUNT\s*\}\}\s*advisory,\s*"
            r"\{\{\s*OK_COUNT\s*\}\}\s*ok,\s*"
            r"\{\{\s*NA_COUNT\s*\}\}\s*n-a",
            template_text,
        )
        assert verdict_line, (
            "Template must render the exact VERDICT line shape including em-dash, "
            "comma separators, and all four count tokens (CI greppability contract)"
        )

    def test_render_marker_present(self, template_text):
        """The renderer must strip the preamble before printing — marker required."""
        assert "BEGIN-RENDER" in template_text, (
            "Template must include a <!-- BEGIN-RENDER --> marker so the renderer "
            "can strip the documentation preamble before printing the report"
        )

    def test_placeholder_style_no_interior_spaces(self, template_text):
        """Placeholders use {{ALL_CAPS}} without interior spaces (matches generate-dag's templates)."""
        # Look for any placeholder that has interior spaces — these would
        # break the renderer's substitution pattern.
        bad_placeholders = re.findall(r"\{\{\s+\w+\s+\}\}", template_text)
        # Note: the template documentation block enumerates placeholders
        # with explanatory text; the BODY (after BEGIN-RENDER) is what must
        # be clean. Split on the marker.
        if "<!-- BEGIN-RENDER -->" in template_text:
            body = template_text.split("<!-- BEGIN-RENDER -->", 1)[1]
            body_bad = re.findall(r"\{\{\s+\w+\s+\}\}", body)
            assert not body_bad, (
                f"Body placeholders must NOT have interior spaces: {body_bad}"
            )


# ---------------------------------------------------------------------------
# Sibling consistency — generate-dag must still emit the IDs we validate
# ---------------------------------------------------------------------------

class TestSiblingConsistency:
    """Validator/producer lock-step: every rule we enforce must be a rule the producer emits to."""

    def test_generate_dag_skill_exists(self):
        assert GENERATE_DAG_SKILL_MD.exists(), (
            "Sibling skill /generate-dag is missing — /validate-dag's cite contract has no upstream"
        )

    def test_generate_dag_citations_reference_doc_exists(self):
        assert RFD_0011_CITATIONS.exists(), (
            "/generate-dag/references/rfd-0011-citations.md missing — validator remediation hints can't resolve"
        )

    def test_validator_enforces_subset_of_producer_standards(self):
        """Every rule listed in validate-dag's standards block must also appear in generate-dag.

        The lock-step contract: the auditor never enforces a rule the
        producer doesn't already emit to. The producer is allowed to
        emit additional ones the validator can't see (e.g. bundle-internal
        DBX-DAB-002).
        """
        validator_text = SKILL_MD.read_text()
        producer_text = GENERATE_DAG_SKILL_MD.read_text()

        # Extract rule IDs from validator's frontmatter (looking for
        # PY-AIRFLOW-NNN and DBX-DAB-NNN tokens in the first 100 lines).
        validator_head = "\n".join(validator_text.splitlines()[:100])
        validator_rules = set(re.findall(r"PY-AIRFLOW-\d{3}|DBX-DAB-\d{3}", validator_head))
        producer_rules = set(re.findall(r"PY-AIRFLOW-\d{3}|DBX-DAB-\d{3}", producer_text))

        missing_in_producer = validator_rules - producer_rules
        assert not missing_in_producer, (
            f"Validator enforces rules the producer doesn't emit to: {missing_in_producer}. "
            "This breaks the lock-step contract."
        )
