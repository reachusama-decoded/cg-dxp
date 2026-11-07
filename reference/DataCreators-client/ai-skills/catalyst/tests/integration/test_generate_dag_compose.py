"""Compose-contract integration test for /generate-dag.

The /generate-dag skill must read a sibling skill's output
(/setup-databricks-asset-bundle's databricks.yml + per-dataset
*.job.yml + variables_<env>.yml) and emit a DAG whose job_name
matches the bundle's deployed convention.

This is structurally a cross-skill contract test, not a unit test.
It does NOT exercise the LLM (the bt harness has no setup.files:
support yet — see OQ-7 in the design spec). Instead, it asserts the
contract is correctly documented in the skill content itself:

- SKILL.md cites the specific bundle file paths the agent must read
- references/compose-with-bundle.md documents the discovery flow with concrete commands
- Pattern A + B templates use the bundle-convention templated job_name
- All three mode behaviours (production/prototype/lift-and-shift) for
  the no-bundle case are spelled out

If any of these structural anchors disappears, the agent will silently
freelance the compose step and emit DAGs that don't match the bundle.
This test catches that before the skill ships into a team's repo.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATE_DAG_DIR = REPO_ROOT / "skills" / "generate-dag"
SKILL_MD = GENERATE_DAG_DIR / "SKILL.md"
COMPOSE_REF = GENERATE_DAG_DIR / "references" / "compose-with-bundle.md"
PATTERN_A = GENERATE_DAG_DIR / "references" / "pattern-dag-factory.md"
PATTERN_B = GENERATE_DAG_DIR / "references" / "pattern-astro-blueprints.md"

# Sibling skill whose output we compose with
SETUP_BUNDLE_DIR = REPO_ROOT / "skills" / "setup-databricks-asset-bundle"
SETUP_BUNDLE_SKILL_MD = SETUP_BUNDLE_DIR / "SKILL.md"

# Bundle file paths the /generate-dag agent is supposed to read.
BUNDLE_ARTIFACTS = [
    "databricks.yml",
    "<dataset>.job.yml",
    "variables_<env>.yml",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL_MD.exists(), f"SKILL.md missing: {SKILL_MD}"
    return SKILL_MD.read_text()


@pytest.fixture(scope="module")
def compose_ref_text() -> str:
    assert COMPOSE_REF.exists(), f"compose ref missing: {COMPOSE_REF}"
    return COMPOSE_REF.read_text()


@pytest.fixture(scope="module")
def pattern_a_text() -> str:
    assert PATTERN_A.exists(), f"Pattern A ref missing: {PATTERN_A}"
    return PATTERN_A.read_text()


@pytest.fixture(scope="module")
def pattern_b_text() -> str:
    assert PATTERN_B.exists(), f"Pattern B ref missing: {PATTERN_B}"
    return PATTERN_B.read_text()


# ---------------------------------------------------------------------------
# SKILL.md must instruct the agent to read bundle artifacts
# ---------------------------------------------------------------------------

class TestSkillMdReferencesBundleArtifacts:
    """The agent's instructions must name the specific files the bundle skill emits."""

    def test_skill_references_databricks_yml(self, skill_text):
        assert "databricks.yml" in skill_text, (
            "/generate-dag SKILL.md must reference databricks.yml — without this the agent can't find the bundle config"
        )

    def test_skill_references_job_yml(self, skill_text):
        # Either the literal `<dataset>.job.yml` template or `*.job.yml`
        assert re.search(r"job\.yml|<dataset>\.job\.yml|<dataset>\.job\.yaml", skill_text), (
            "/generate-dag SKILL.md must reference the per-dataset *.job.yml file path"
        )

    def test_skill_references_variables_env_yml(self, skill_text):
        assert re.search(r"variables_<env>\.yml|variables/variables_", skill_text), (
            "/generate-dag SKILL.md must reference variables/variables_<env>.yml for per-env prefix discovery"
        )

    def test_skill_declares_dependency_on_setup_databricks_asset_bundle(self, skill_text):
        # Frontmatter dependencies list
        assert "setup-databricks-asset-bundle" in skill_text, (
            "/generate-dag must declare setup-databricks-asset-bundle in metadata.dependencies"
        )


# ---------------------------------------------------------------------------
# compose-with-bundle.md must document the discovery flow concretely
# ---------------------------------------------------------------------------

class TestComposeReferenceDocumentsDiscovery:
    """The reference must spell out HOW to discover the job name from bundle files."""

    def test_compose_ref_shows_databricks_yml_read(self, compose_ref_text):
        assert "cat data_products/" in compose_ref_text or "cat databricks.yml" in compose_ref_text, (
            "compose-with-bundle.md must show concrete commands to read bundle files"
        )

    def test_compose_ref_documents_databricks_job_prefix(self, compose_ref_text):
        assert "databricks_job_prefix" in compose_ref_text, (
            "compose ref must document the databricks_job_prefix var that ties DAG to bundle"
        )

    def test_compose_ref_shows_templated_job_name(self, compose_ref_text):
        # The canonical templated form. Either form is acceptable.
        pattern = r"\{\{\s*var\.value\.databricks_job_prefix\s*\}\}"
        assert re.search(pattern, compose_ref_text), (
            "compose ref must show templated job_name using {{ var.value.databricks_job_prefix }}"
        )

    def test_compose_ref_documents_all_three_no_bundle_modes(self, compose_ref_text):
        """When databricks.yml is absent, behaviour must be defined for production / prototype / lift-and-shift."""
        text_lower = compose_ref_text.lower()
        assert "production" in text_lower, "compose ref must document production-mode no-bundle behaviour"
        assert "prototype" in text_lower, "compose ref must document prototype-mode no-bundle behaviour"
        assert "lift-and-shift" in text_lower, "compose ref must document lift-and-shift no-bundle behaviour"

    def test_compose_ref_production_mode_refuses(self, compose_ref_text):
        """Production mode without bundle must STOP, not emit placeholder."""
        # Find the production-mode block
        prod_section = re.search(
            r"production.{0,100}(?:STOP|stop|refuse|refuses)",
            compose_ref_text,
            re.IGNORECASE | re.DOTALL,
        )
        assert prod_section, (
            "compose ref must say production mode STOPs/refuses when no bundle exists; instead emitting a placeholder there is unsafe"
        )

    def test_compose_ref_prototype_mode_uses_placeholder(self, compose_ref_text):
        """Prototype mode without bundle must emit a placeholder + advisory."""
        proto_section = re.search(
            r"prototype.{0,200}(?:placeholder|TODO|warn)",
            compose_ref_text,
            re.IGNORECASE | re.DOTALL,
        )
        assert proto_section, (
            "compose ref must say prototype mode emits a placeholder with a TODO/warning when no bundle exists"
        )


# ---------------------------------------------------------------------------
# Pattern templates must use the bundle-convention templated job_name
# ---------------------------------------------------------------------------

class TestPatternTemplatesUseBundleConvention:
    """Both emission patterns must template job_name with the bundle var."""

    TEMPLATED_JOB_NAME = re.compile(
        r'job_name:\s*"\{\{\s*var\.value\.(?:get\(\'databricks_job_prefix\',\s*\'\'\)|databricks_job_prefix)\s*\}\}<dataset>_job"'
    )

    def test_pattern_a_templates_job_name(self, pattern_a_text):
        assert self.TEMPLATED_JOB_NAME.search(pattern_a_text), (
            "Pattern A (dag-factory) template must use the bundle-templated job_name"
        )

    def test_pattern_b_templates_job_name(self, pattern_b_text):
        assert self.TEMPLATED_JOB_NAME.search(pattern_b_text), (
            "Pattern B (astro-blueprints) template must use the bundle-templated job_name"
        )

    def test_pattern_a_references_databricks_conn_id(self, pattern_a_text):
        assert "databricks_conn_id" in pattern_a_text, (
            "Pattern A must reference databricks_conn_id (Astronomer Connection — RFD 0011 §8)"
        )

    def test_pattern_b_references_databricks_conn_id(self, pattern_b_text):
        assert "databricks_conn_id" in pattern_b_text, (
            "Pattern B must reference databricks_conn_id (Astronomer Connection — RFD 0011 §8)"
        )


# ---------------------------------------------------------------------------
# Sibling skill /setup-databricks-asset-bundle must emit the convention we depend on
# ---------------------------------------------------------------------------

class TestSiblingSkillEmitsBundleConvention:
    """Verify /setup-databricks-asset-bundle still emits the convention /generate-dag depends on.

    If this test fails, /generate-dag's compose contract has been broken upstream:
    the bundle skill has stopped emitting databricks_job_prefix or has renamed
    the per-dataset job key pattern.
    """

    def test_setup_bundle_skill_exists(self):
        assert SETUP_BUNDLE_SKILL_MD.exists(), (
            "Sibling skill /setup-databricks-asset-bundle is missing — /generate-dag's compose contract has no upstream"
        )

    def test_setup_bundle_references_databricks_job_prefix(self):
        """The bundle skill must emit a databricks_job_prefix variable for /generate-dag to reference."""
        text = SETUP_BUNDLE_SKILL_MD.read_text()
        assert "databricks_job_prefix" in text, (
            "/setup-databricks-asset-bundle must document the databricks_job_prefix variable that /generate-dag's compose contract depends on"
        )

    def test_setup_bundle_references_per_dataset_job_yml(self):
        """The bundle skill must emit per-dataset job.yml files at the canonical path."""
        text = SETUP_BUNDLE_SKILL_MD.read_text()
        # Either form of the per-dataset path is acceptable
        assert re.search(r"datasets/[^/\s]+/bundle|\<dataset>\.job\.yml|dataset.*bundle", text, re.IGNORECASE), (
            "/setup-databricks-asset-bundle must emit per-dataset *.job.yml — that's the file /generate-dag reads to discover job name"
        )
