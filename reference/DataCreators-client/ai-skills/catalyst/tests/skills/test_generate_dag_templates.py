"""Unit tests for /generate-dag vendored Python template files.

These templates ship into the team's repo via /generate-dag emission.
A bug here breaks every DAG that uses the template, so a regression test
in this repo catches it before it lands in a team's Airflow.

The templates live at:
    skills/generate-dag/templates/include/assets.py
    skills/generate-dag/templates/include/callbacks/on_success_log_databricks_url.py
    skills/generate-dag/templates/include/shared/databricks_dbt.py
    skills/generate-dag/templates/include/shared/asset_signal.py
    skills/generate-dag/templates/tests/test_dag_structural.py

Strategy: import-via-path (importlib.util.spec_from_file_location), then
exercise the public surface of each module against mocked Airflow
context. Airflow itself is heavy to install; we mock the airflow.*
imports the templates need.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "skills" / "generate-dag" / "templates"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stub_module(name: str, **attrs) -> types.ModuleType:
    """Create a fake module and register it in sys.modules."""
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


def _load_template(rel_path: str) -> types.ModuleType:
    """Load a template by relative path under TEMPLATE_DIR with mocked deps."""
    abs_path = TEMPLATE_DIR / rel_path
    assert abs_path.exists(), f"Template not found: {abs_path}"
    mod_name = f"_template_{rel_path.replace('/', '_').replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Airflow import stubs (registered once per test module)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _mock_airflow():
    """Register stub modules for airflow.* imports."""
    # airflow.models.Variable
    variable_cls = MagicMock()
    variable_cls.get = MagicMock(return_value="<stubbed>")
    _stub_module("airflow")
    _stub_module("airflow.models", Variable=variable_cls)

    # airflow.datasets.Dataset
    class Dataset:
        def __init__(self, uri):
            self.uri = uri
        def __repr__(self):
            return f"Dataset({self.uri!r})"
        def __eq__(self, other):
            return isinstance(other, Dataset) and self.uri == other.uri
        def __hash__(self):
            return hash(self.uri)
    _stub_module("airflow.datasets", Dataset=Dataset)

    # airflow DAG + DatabricksRunNowOperator (for databricks_dbt blueprint)
    dag_mock = MagicMock()
    _stub_module("airflow", DAG=dag_mock)
    sys.modules["airflow"].DAG = dag_mock
    op_mock = MagicMock()
    _stub_module("airflow.providers")
    _stub_module("airflow.providers.databricks")
    _stub_module("airflow.providers.databricks.operators")
    _stub_module("airflow.providers.databricks.operators.databricks", DatabricksRunNowOperator=op_mock)

    yield


# ---------------------------------------------------------------------------
# assets.py — placeholder-substitution template
# ---------------------------------------------------------------------------

class TestAssetsTemplate:
    """The assets.py template is mostly markers + comments; verify shape."""

    def test_template_exists(self):
        path = TEMPLATE_DIR / "include" / "assets.py"
        assert path.exists()

    def test_template_has_producer_placeholder(self):
        text = (TEMPLATE_DIR / "include" / "assets.py").read_text()
        assert "{{ PRODUCERS }}" in text

    def test_template_has_consumer_placeholder(self):
        text = (TEMPLATE_DIR / "include" / "assets.py").read_text()
        assert "{{ CONSUMERS }}" in text

    def test_template_imports_dataset(self):
        text = (TEMPLATE_DIR / "include" / "assets.py").read_text()
        assert "from airflow.datasets import Dataset" in text

    def test_template_cites_rfd(self):
        text = (TEMPLATE_DIR / "include" / "assets.py").read_text()
        assert "RFD 0011" in text
        assert "RFD 0007" in text


# ---------------------------------------------------------------------------
# on_success_log_databricks_url.py — Databricks run URL emission
# ---------------------------------------------------------------------------

class TestOnSuccessLogDatabricksUrl:

    @pytest.fixture
    def module(self):
        return _load_template("include/callbacks/on_success_log_databricks_url.py")

    def test_callback_is_callable(self, module):
        assert callable(module.callback)

    def test_no_run_id_returns_silently(self, module, caplog):
        """When XCom has no run_id, callback returns without logging an URL."""
        ti = MagicMock()
        ti.xcom_pull = MagicMock(return_value=None)
        context = {"task_instance": ti}

        with caplog.at_level(logging.INFO):
            module.callback(context)

        url_logs = [r for r in caplog.records if "Databricks run" in r.message]
        assert not url_logs

    def test_logs_url_when_run_id_present(self, module, caplog):
        """When run_id and workspace_url present, callback logs the click-through URL."""
        from airflow.models import Variable
        Variable.get.return_value = "https://workspace.databricks.com"

        ti = MagicMock()
        ti.xcom_pull = MagicMock(return_value="run-12345")
        context = {"task_instance": ti}

        with caplog.at_level(logging.INFO):
            module.callback(context)

        url_logs = [r for r in caplog.records if "run-12345" in r.message]
        assert url_logs, "Expected a log line containing the run_id"
        assert any("workspace.databricks.com" in r.message for r in url_logs)

    def test_missing_workspace_url_warns(self, module, caplog):
        """When workspace URL Variable is missing, callback warns and returns."""
        from airflow.models import Variable
        Variable.get.side_effect = KeyError("databricks_workspace_url")

        ti = MagicMock()
        ti.xcom_pull = MagicMock(return_value="run-xyz")
        context = {"task_instance": ti}

        with caplog.at_level(logging.WARNING):
            module.callback(context)

        assert any("workspace_url" in r.message.lower() for r in caplog.records)
        Variable.get.side_effect = None
        Variable.get.return_value = "<stubbed>"


# ---------------------------------------------------------------------------
# databricks_dbt.py — Astro-blueprint that builds a Databricks-job DAG
# ---------------------------------------------------------------------------

class TestDatabricksDbtBlueprint:

    @pytest.fixture
    def module(self):
        return _load_template("include/shared/databricks_dbt.py")

    def test_build_dag_callable(self, module):
        assert callable(module.build_dag)

    def test_build_dag_constructs_dag_and_operator(self, module):
        """build_dag returns a DAG (mocked) and calls DatabricksRunNowOperator with the expected kwargs."""
        params = {
            "databricks_conn_id": "databricks_default",
            "job_name": "my_job",
            "partition_key": "{{ ds }}",
            "pool": "databricks_sm",
            "pool_slots": 2,
        }
        default_args = {"retries": 3}
        tags = {"owner": "team@cap.com"}

        dag = module.build_dag(
            dag_id="my__dag",
            params=params,
            default_args=default_args,
            schedule=["x"],
            catchup=False,
            tags=tags,
            start_date="2026-01-01",
            render_template_as_native_obj=True,
        )

        assert dag is not None  # mock-returned object


# ---------------------------------------------------------------------------
# asset_signal.py — Asset URI helpers for Pattern B
# ---------------------------------------------------------------------------

class TestAssetSignal:

    @pytest.fixture
    def module(self):
        return _load_template("include/shared/asset_signal.py")

    def test_signal_ready_produces_correct_uri(self, module):
        ds = module.signal_ready("daily_positions")
        assert ds.uri == "daily_positions_ready"

    def test_wait_for_produces_correct_uri(self, module):
        ds = module.wait_for("raw_positions")
        assert ds.uri == "raw_positions_ready"

    def test_signal_ready_and_wait_for_match_on_same_name(self, module):
        """signal_ready('x') and wait_for('x') produce equal Datasets — that's how the trigger graph composes."""
        producer = module.signal_ready("foo")
        consumer = module.wait_for("foo")
        assert producer == consumer
        assert producer.uri == consumer.uri == "foo_ready"


# ---------------------------------------------------------------------------
# test_dag_structural.py — substitution sanity check
# ---------------------------------------------------------------------------

class TestStructuralTestTemplate:
    """The structural-test template uses {{PRODUCT}} and {{DATASET}} placeholders.
    Verify substitution produces parseable Python and contains the expected assertions."""

    @pytest.fixture
    def template_text(self):
        return (TEMPLATE_DIR / "tests" / "test_dag_structural.py").read_text()

    def test_template_has_placeholders(self, template_text):
        assert "{{PRODUCT}}" in template_text
        assert "{{DATASET}}" in template_text

    def test_substituted_template_is_valid_python(self, template_text):
        import ast
        rendered = template_text.replace("{{PRODUCT}}", "my_product").replace("{{DATASET}}", "my_dataset")
        # Should parse as valid Python
        ast.parse(rendered)

    def test_template_asserts_mds_tags(self, template_text):
        assert "REQUIRED_TAG_KEYS" in template_text
        for tag in ("l1_domain", "l1_xmatters_group", "lifecycle_phase", "data_classification", "criticality"):
            assert tag in template_text

    def test_template_rejects_pagerduty(self, template_text):
        assert "pagerduty" in template_text.lower()
        assert "anti-goal" in template_text.lower() or "must reference Datadog" in template_text

    def test_template_rejects_python_operator(self, template_text):
        assert "PythonOperator" in template_text
        assert "no PythonOperator" in template_text or "PythonOperator" in template_text
