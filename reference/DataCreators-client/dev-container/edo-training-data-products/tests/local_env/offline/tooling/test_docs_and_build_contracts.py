from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_pipeline_uses_environment_specific_databricks_hosts() -> None:
    pipeline = _read(".harness/edo-training-data-products-pipeline.yaml")
    hosts = re.findall(r"^\s+DATABRICKS_HOST:\s+(\S+)$", pipeline, re.MULTILINE)
    assert hosts == [
        "https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com",
        "https://cg-db-aa00003661-dev-us-west-2.cloud.databricks.com",
        "https://cg-db-aa00003661-sqa-us-east-1.cloud.databricks.com",
        "https://cg-db-aa00003661-sqa-us-west-2.cloud.databricks.com",
        "https://cg-db-aa00003661-prd-us-east-1.cloud.databricks.com",
        "https://cg-db-aa00003661-prd-us-west-2.cloud.databricks.com",
    ]


def test_dpc_check_matches_documented_health_contract() -> None:
    script = _read(".devcontainer/check.sh")
    for marker in (
        'section "CLI tools"',
        'section "Inner dockerd (DinD)"',
        'section "TLS / corp CA plumbing"',
        'section "Astro build readiness"',
        'section "Local Airflow runtime"',
        'section "Data product scaffolding"',
        'section "Databricks auth"',
    ):
        assert marker in script
    for token in (
        'python on PATH',
        'astro on PATH',
        'databricks on PATH',
        'dbt on PATH',
        'docker CLI on PATH',
        'dbt-core installed',
        'dbt-databricks installed',
        'astro scheduler container running',
        'astro api-server container running',
    ):
        assert token in script
    assert "/cacert.pem" in script
    assert "cgrepo-aws.capgroup.com/repository/cgpypi/simple" in script
    assert "databricks current-user me" in script
    assert "dbt_wrapper.py" in script
    assert "wait_for_docker_ready" not in script
    assert "airflow_settings.yaml" in script
    assert "dbt_profiles/profiles.yml" in script
    assert "sitecustomize loaded" in script


def test_dpc_check_prevents_interactive_auth_hangs() -> None:
    script = _read(".devcontainer/check.sh")
    assert "run_with_timeout()" in script
    assert "run_with_timeout 20 env DBT_HOST=https://placeholder" in script
    assert "DATABRICKS_AUTH_TYPE=pat" in script
    assert "Databricks OAuth session may be expired or missing" in script
    assert 'soft_check "databricks current-user me works"  run_with_timeout 20 databricks current-user me' in script


def test_integration_marker_is_registered() -> None:
    pytest_ini = _read("pytest.ini")
    assert "markers =" in pytest_ini
    assert "integration:" in pytest_ini


def test_mise_excludes_deprecated_setup_tasks() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."setup:host-path"]' not in mise
    assert '[tasks."setup:normalize-env"]' not in mise
    assert '[tasks."setup:databricks-oauth"]' not in mise
    assert '[tasks."setup:databricks"]' in mise
    assert 'flag "--pat"' in mise


def test_oauth_setup_no_longer_requires_env_bootstrap() -> None:
    mise = _read(".mise.toml")
    block = mise.split('[tasks."setup:databricks"]', 1)[1].split("[tasks.", 1)[0]
    assert "depends =" not in block


def test_full_setup_does_not_block_on_interactive_oauth() -> None:
    mise = _read(".mise.toml")
    assert '[tasks.setup]' in mise
    assert "setup:databricks" not in mise.split('[tasks.setup]')[-1].split('[tasks.', 1)[0]


def test_astro_onbuild_is_forced_to_pip_mode() -> None:
    req = _read("requirements.txt")
    assert "ASTRO_RUNTIME_USE_PIP" in req


def test_astro_requirements_include_corp_trusted_hosts() -> None:
    req = _read("requirements.txt")
    assert "--trusted-host pip.astronomer.io" in req
    assert "--trusted-host pypi.org" in req
    assert "--trusted-host files.pythonhosted.org" in req


def test_dockerfile_uses_buildkit_cache_mounts_for_apt_and_pip() -> None:
    dockerfile = _read("Dockerfile")
    assert "--mount=type=cache,target=/var/cache/apt" in dockerfile
    assert "--mount=type=cache,target=/var/lib/apt/lists" in dockerfile
    assert "--mount=type=cache,target=/root/.cache/pip" in dockerfile
    assert "--mount=type=cache,target=/home/astro/.cache/pip" in dockerfile


def test_devcontainer_dockerfile_uses_buildkit_cache_mounts_for_apk_and_python() -> None:
    dockerfile = _read(".devcontainer/Dockerfile")
    assert "--mount=type=cache,target=/var/cache/apk" in dockerfile
    assert "--mount=type=cache,target=/root/.cache/pip" in dockerfile
    assert "--mount=type=cache,target=/root/.cache/uv" in dockerfile


def test_astro_runtime_includes_blueprint_loader_dependency() -> None:
    req = _read("requirements-pypi.txt")
    assert "airflow-blueprint" in req


def test_blueprints_loader_uses_airflow3_operator_link_import() -> None:
    loader = _read("data_products/blueprints_loader.py")
    assert "from airflow.sdk import BaseOperatorLink" in loader
    assert "from airflow.models.baseoperator import BaseOperatorLink" not in loader


def test_blueprints_loader_uses_airflow_dags_folder_for_config_root() -> None:
    loader = _read("data_products/blueprints_loader.py")
    assert "AIRFLOW__CORE__DAGS_FOLDER" in loader


def test_blueprints_loader_applies_required_cost_tags_for_policy() -> None:
    loader = _read("data_products/blueprints_loader.py")
    assert "usage-id:" in loader
    assert "cost-center:" in loader


def test_setup_python_deps_installs_sitecustomize_into_venv() -> None:
    script = _read(".devcontainer/utils/setup-python-deps.sh")
    assert ".devcontainer/sitecustomize.py" in script
    assert "sitecustomize.py" in script
    assert ".venv/bin/python" in script
    assert "/opt/venv/bin/python" in script
    assert "certifi.where()" in script
