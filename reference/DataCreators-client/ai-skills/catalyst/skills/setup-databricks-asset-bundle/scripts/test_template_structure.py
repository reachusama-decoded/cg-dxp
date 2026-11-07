#!/usr/bin/env python3
"""CI structural test for the setup-databricks-asset-bundle templates.

Renders `templates/` with fixture placeholder values into a tmpdir, then
runs the emitted `test_dab_structural.py` against that tree (via pytest
subprocess) to catch template-side regressions before they reach a
consumer repo.

Complements `templates/tests/test_dab_structural.py`, which only runs
inside the user's repo after `mode=new-dataset` emission. Catalyst CI
needs to catch template regressions that wouldn't surface until a
downstream user re-renders, so this test renders + asserts here.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = SKILL_DIR / "templates"

# Minimal fixture: every placeholder the templates reference must appear
# here. A missing placeholder lands as a literal `{{NAME}}` in the
# rendered output and is caught by `test_no_unresolved_placeholders`.
FIXTURE_SUBS = {
    "PRODUCT": "sample_product",
    "DATASET": "sample_dataset",
    "PROJECT_NAME": "sample_project",
    "PROJECT_TEAM": "sample_team",
    "ATM_ID": "ATM00000",
    "APP_NAME": "sample_app",
    "CHECKPOINT_TABLE_NAME": "standard_dataset_checkpoints",
    # Dev
    "DEV_WORKSPACE_HOST": "dev.example.cloud.databricks.com",
    "DEV_PROFILE": "dev-profile",
    "DEV_SQL_WAREHOUSE_HTTP_PATH": "/sql/1.0/warehouses/aaaaaaaaaaaaaaaa",
    "DEV_SQL_WAREHOUSE_ID": "aaaaaaaaaaaaaaaa",
    "DEV_KAFKA_SECRET_SCOPE": "dev-kafka-scope",
    "DEV_KAFKA_SECRET_ARN": "arn:dev:kafka",
    "DEV_ROOTCA_SECRET_ARN": "arn:dev:rootca",
    "DEV_DATA_NOTIFY_TOPIC": "dev.notify.topic",
    "DEV_MSK_BOOTSTRAP_BROKERS": "dev-broker:9096",
    "DEV_SCHEMA_REGISTRY_URL": "https://schema-registry.dev.example",
    "DEV_ZONE_BUCKET": "s3://dev-zone",
    "DEV_UTIL_BUCKET": "dev-util",
    "DEV_DEFAULT_CATALOG": "sample_dev",
    "DEV_DEFAULT_SCHEMA": "sample_ref",
    "DEV_CHECKPOINT_SCHEMA": "cspn_sys",
    "DEV_CLUSTER_ID": "0000-000000-aaaaaaaa",
    "DEV_CASPIAN_CATALOG": "caspian_dev",
    "DEV_APP_CATALOG": "sample_app_dev",
    # SQA
    "SQA_WORKSPACE_HOST": "sqa.example.cloud.databricks.com",
    "SQA_SQL_WAREHOUSE_HTTP_PATH": "/sql/1.0/warehouses/bbbbbbbbbbbbbbbb",
    "SQA_SQL_WAREHOUSE_ID": "bbbbbbbbbbbbbbbb",
    "SQA_KAFKA_SECRET_SCOPE": "sqa-kafka-scope",
    "SQA_KAFKA_SECRET_ARN": "arn:sqa:kafka",
    "SQA_ROOTCA_SECRET_ARN": "arn:sqa:rootca",
    "SQA_DATA_NOTIFY_TOPIC": "sqa.notify.topic",
    "SQA_MSK_BOOTSTRAP_BROKERS": "sqa-broker:9096",
    "SQA_SCHEMA_REGISTRY_URL": "https://schema-registry.sqa.example",
    "SQA_ZONE_BUCKET": "s3://sqa-zone",
    "SQA_UTIL_BUCKET": "sqa-util",
    "SQA_DEFAULT_CATALOG": "sample_sqa",
    "SQA_DEFAULT_SCHEMA": "sample_ref",
    "SQA_CHECKPOINT_SCHEMA": "cspn_sys",
    "SQA_CLUSTER_ID": "0000-000000-bbbbbbbb",
    "SQA_CASPIAN_CATALOG": "caspian_sqa",
    "SQA_APP_CATALOG": "sample_app_sqa",
    "SQA_TARGET_SCHEMA": "sqa_user",
    # PRD
    "PRD_WORKSPACE_HOST": "prd.example.cloud.databricks.com",
    "PRD_SQL_WAREHOUSE_HTTP_PATH": "/sql/1.0/warehouses/cccccccccccccccc",
    "PRD_SQL_WAREHOUSE_ID": "cccccccccccccccc",
    "PRD_KAFKA_SECRET_SCOPE": "prd-kafka-scope",
    "PRD_KAFKA_SECRET_ARN": "arn:prd:kafka",
    "PRD_ROOTCA_SECRET_ARN": "arn:prd:rootca",
    "PRD_DATA_NOTIFY_TOPIC": "prd.notify.topic",
    "PRD_MSK_BOOTSTRAP_BROKERS": "prd-broker:9096",
    "PRD_SCHEMA_REGISTRY_URL": "https://schema-registry.prd.example",
    "PRD_ZONE_BUCKET": "s3://prd-zone",
    "PRD_UTIL_BUCKET": "prd-util",
    "PRD_DEFAULT_CATALOG": "sample_prd",
    "PRD_DEFAULT_SCHEMA": "sample_ref",
    "PRD_CHECKPOINT_SCHEMA": "cspn_sys",
    "PRD_CLUSTER_ID": "0000-000000-cccccccc",
    "PRD_CASPIAN_CATALOG": "caspian_prd",
    "PRD_APP_CATALOG": "sample_app_prd",
    "PRD_TARGET_SCHEMA": "prd_user",
    # DR
    "DEV_DR_WORKSPACE_HOST": "dev-dr.example.cloud.databricks.com",
    "DEV_DR_APP_CATALOG": "sample_app_dev_dr",
    "DEV_DR_TARGET_SCHEMA": "dev_dr_user",
    "DEV_DR_CHECKPOINT_SCHEMA": "cspn_sys",
    "SQA_DR_WORKSPACE_HOST": "sqa-dr.example.cloud.databricks.com",
    "SQA_DR_APP_CATALOG": "sample_app_sqa_dr",
    "SQA_DR_TARGET_SCHEMA": "sqa_dr_user",
    "SQA_DR_CHECKPOINT_SCHEMA": "cspn_sys",
    "PRD_DR_WORKSPACE_HOST": "prd-dr.example.cloud.databricks.com",
    "PRD_DR_APP_CATALOG": "sample_app_prd_dr",
    "PRD_DR_TARGET_SCHEMA": "prd_dr_user",
    "PRD_DR_CHECKPOINT_SCHEMA": "cspn_sys",
    # DQ job ODCS-sourced values (filled per-dataset at emission time;
    # fixture values are placeholders for CI rendering).
    "DQ_APPLICATION_NAME": "sample-app",
    "DATASET_RULESET_DATASET_NAME": "cspn_sample_v1_base",
    "DATASET_RULESET_NAME": "cspn_dim_sample_v1_base",
    "DQ_SCHEMA_TEMPLATE": "${var.app_catalog}.${var.data_product_name}",
}

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


def _render(text: str, subs: dict) -> str:
    return _PLACEHOLDER_RE.sub(lambda m: subs.get(m.group(1), m.group(0)), text)


def _render_skill_into(dst: Path, subs: dict) -> None:
    """Render the skill's templates into `dst/data_products/<PRODUCT>/`."""
    product = subs["PRODUCT"]
    dataset = subs["DATASET"]
    pdir = dst / "data_products" / product
    mapping = [
        (TEMPLATES_DIR / "databricks.yml", pdir / "databricks.yml"),
        (TEMPLATES_DIR / "variables" / "variables.yml", pdir / "variables" / "variables.yml"),
        (TEMPLATES_DIR / "variables" / "clusters.yml", pdir / "variables" / "clusters.yml"),
        (TEMPLATES_DIR / "datasets" / "dataset.job.yml",
         pdir / "datasets" / dataset / "bundle" / f"{dataset}.job.yml"),
        (TEMPLATES_DIR / "datasets" / "dataset_dq.job.yml",
         pdir / "datasets" / dataset / "bundle" / f"{dataset}_dq.job.yml"),
        (TEMPLATES_DIR / "tests" / "test_dab_structural.py",
         dst / "tests" / "dab" / f"test_{dataset}_dab_structural.py"),
    ]
    for src, target in mapping:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render(src.read_text(), subs))


class TemplateStructuralTests(unittest.TestCase):
    """Render templates with fixture values, then run the emitted
    structural test against the rendered tree.

    Any failure here means a template change broke an invariant that
    the user's CI would catch only after `mode=new-dataset` emission —
    catalyst CI catches it at template-merge time instead.
    """

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo_root = Path(cls._tmp.name)
        _render_skill_into(cls.repo_root, FIXTURE_SUBS)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_no_unresolved_placeholders(self):
        """No `{{NAME}}` literals survive in any emitted file.

        Catches missing FIXTURE_SUBS keys or template references to
        placeholders that haven't been declared in SKILL.md.
        """
        offenders = []
        for path in self.repo_root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(errors="replace")
            for m in _PLACEHOLDER_RE.finditer(text):
                offenders.append(f"{path.relative_to(self.repo_root)}: {{{{{m.group(1)}}}}}")
        self.assertFalse(
            offenders,
            "Rendered output contains unresolved {{…}} placeholders; either add the "
            "key to FIXTURE_SUBS or remove the reference from the template:\n  "
            + "\n  ".join(offenders),
        )

    def test_structural_pytest_passes_against_rendered_tree(self):
        """Run the emitted `test_<dataset>_dab_structural.py` via pytest.

        Exit code 0 = all structural assertions pass against the rendered
        output. Non-zero = template regression.
        """
        dataset = FIXTURE_SUBS["DATASET"]
        test_path = self.repo_root / "tests" / "dab" / f"test_{dataset}_dab_structural.py"
        self.assertTrue(test_path.exists(), f"Rendered structural test not found at {test_path}")

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", str(test_path)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            f"Structural pytest failed against rendered templates:\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
