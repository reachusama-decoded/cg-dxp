from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
pytestmark = pytest.mark.airflow


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_airflow_setup_tolerates_a_missing_template() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert 'if [ ! -f "$EXAMPLE_FILE" ]; then' in script
    assert "Airflow settings template not found" in script


def test_airflow_settings_script_and_docs_use_the_tracked_template() -> None:
    template_path = ".airflow/airflow_settings.yaml.example"
    assert (REPO_ROOT / template_path).is_file()

    setup = _read(".devcontainer/utils/setup-airflow-settings.sh")
    guide = _read(".devcontainer/README.md")
    assert f'EXAMPLE_FILE="{template_path}"' in setup
    assert 'SETTINGS_FILE="airflow_settings.yaml"' in setup
    assert template_path in guide


def test_airflow_settings_template_includes_both_databricks_connections() -> None:
    template = _read(".airflow/airflow_settings.yaml.example")
    assert "conn_id: 'databricks_default'" in template
    assert "conn_id: 'caspian-training-databricks'" in template
    assert template.count("conn_type: 'databricks'") == 2
    assert template.count("conn_host: ''") == 2
    assert template.count("conn_password: ''") == 2


def test_airflow_settings_script_keeps_oauth_tokens_out_of_airflow_settings() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert 'DPC_DATABRICKS_AUTH_MODE' in script
    assert 'auth_mode == "pat"' in script
    assert 'auth_mode == "oauth"' in script
    assert "databricks auth token --profile DEFAULT --output json" in script
    assert "OAuth mode detected; refreshed Airflow connection passwords with a short-lived token" in script
    assert 'PAT mode detected; wrote both Databricks connection passwords' in script
    assert 'if host and token:' not in script


def test_docs_state_oauth_token_not_persisted_in_airflow_settings() -> None:
    readme = _read(".devcontainer/README.md")
    assert "does not persist OAuth access tokens in airflow_settings.yaml" in readme


def test_airflow_settings_oauth_mode_does_not_persist_access_token(tmp_path) -> None:
    script = REPO_ROOT / ".devcontainer/utils/setup-airflow-settings.sh"
    workspace = tmp_path / "ws"
    (workspace / ".airflow").mkdir(parents=True, exist_ok=True)
    (workspace / ".airflow/airflow_settings.yaml.example").write_text(
        _read(".airflow/airflow_settings.yaml.example"),
        encoding="utf-8",
    )
    (workspace / "airflow_settings.yaml").write_text(
        _read(".airflow/airflow_settings.yaml.example"),
        encoding="utf-8",
    )
    (workspace / ".config/dpc").mkdir(parents=True, exist_ok=True)
    (workspace / ".config/dpc/databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://workspace\n",
        encoding="utf-8",
    )
    fake_bin = workspace / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    (fake_bin / "databricks").write_text(
        "#!/usr/bin/env bash\n"
        "if [ \"$1\" = \"auth\" ] && [ \"$2\" = \"token\" ]; then\n"
        "  echo '{\"access_token\":\"abc.jwt.token\"}'\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = \"current-user\" ]; then\n"
        "  echo '{\"userName\":\"dev@capgroup.com\"}'\n"
        "  exit 0\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    (fake_bin / "databricks").chmod(0o755)

    import os
    import subprocess
    subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        check=True,
        env={**os.environ, "HOME": str(workspace), "PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )
    rendered = (workspace / "airflow_settings.yaml").read_text(encoding="utf-8")
    assert "abc.jwt.token" not in rendered


def test_airflow_settings_oauth_refresher_launch_uses_a_clean_token_env() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert 'env -u DATABRICKS_TOKEN nohup "$REFRESHER" --loop' in script
    assert 'export DPC_DATABRICKS_AUTH_MODE DATABRICKS_HOST DBT_HOST DATABRICKS_TOKEN' not in script


def test_airflow_settings_oauth_refresher_starts_before_optional_username_lookup() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    refresher = 'env -u DATABRICKS_TOKEN nohup "$REFRESHER" --loop'
    current_user_lookup = 'DBX_JSON=$(databricks current-user me --profile DEFAULT --output json 2>/dev/null || true)'
    assert refresher in script
    assert current_user_lookup in script
    assert script.index(refresher) < script.index(current_user_lookup)


def test_setup_databricks_oauth_bootstraps_airflow_settings() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "setup-airflow-settings.sh" in script
    assert "Setting up Airflow Databricks connections..." in script


def test_airflow_settings_script_does_not_clobber_existing_connection_passwords_without_token(
    tmp_path,
) -> None:
    script = REPO_ROOT / ".devcontainer/utils/setup-airflow-settings.sh"
    workspace = tmp_path / "workspace"
    (workspace / ".airflow").mkdir(parents=True)
    (workspace / ".airflow/airflow_settings.yaml.example").write_text(
        _read(".airflow/airflow_settings.yaml.example"),
        encoding="utf-8",
    )
    (workspace / "airflow_settings.yaml").write_text(
        """airflow:
  connections:
    - conn_id: 'databricks_default'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
    - conn_id: 'caspian-training-databricks'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
  pools: []
  variables:
    - variable_name: databricks_job_prefix
      variable_value: ""
""",
        encoding="utf-8",
    )

    home = tmp_path / "home"
    (home / ".config/dpc").mkdir(parents=True)
    (home / ".config/dpc/databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )

    import subprocess

    result = subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    rendered = (workspace / "airflow_settings.yaml").read_text(encoding="utf-8")
    # In OAuth mode without a minted token, connection passwords must be scrubbed
    # to avoid persisting tokens on disk.
    assert "conn_password: 'existing-token'" not in rendered
    assert "conn_password: ''" in rendered


def test_airflow_settings_script_rewrites_connections_with_minted_oauth_token(tmp_path) -> None:
    script = REPO_ROOT / ".devcontainer/utils/setup-airflow-settings.sh"
    workspace = tmp_path / "workspace"
    (workspace / ".airflow").mkdir(parents=True)
    (workspace / "airflow_settings.yaml").write_text(
        """airflow:
  connections:
    - conn_id: 'databricks_default'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
    - conn_id: 'caspian-training-databricks'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
  pools: []
  variables:
    - variable_name: databricks_job_prefix
      variable_value: ""
""",
        encoding="utf-8",
    )

    home = tmp_path / "home"
    (home / ".config/dpc").mkdir(parents=True)
    (home / ".config/dpc/databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )
    (home / ".databrickscfg").write_text(
        "[DEFAULT]\n"
        "host = https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    databricks_stub = bin_dir / "databricks"
    databricks_stub.write_text(
        """#!/bin/bash
set -e
if [ "$1" = "auth" ] && [ "$2" = "token" ]; then
  cat <<'JSON'
{"access_token":"eyJ.test.oauth.token","token_type":"Bearer","expiry":"2030-01-01T00:00:00Z"}
JSON
  exit 0
fi
if [ "$1" = "current-user" ] && [ "$2" = "me" ]; then
  cat <<'JSON'
{"userName":"tester@example.com"}
JSON
  exit 0
fi
echo "unexpected databricks args: $*" >&2
exit 1
""",
        encoding="utf-8",
    )
    databricks_stub.chmod(0o755)

    import subprocess

    result = subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        env={
            "HOME": str(home),
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "DPC_SKIP_OAUTH_REFRESH": "1",
        },
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    rendered = (workspace / "airflow_settings.yaml").read_text(encoding="utf-8")
    assert "eyJ.test.oauth.token" not in rendered
    assert "conn_host: 'https://example.cloud.databricks.com'" in rendered
    assert "conn_login: ''" in rendered


def test_airflow_settings_script_rewrites_connections_with_pat_token_in_pat_mode(tmp_path) -> None:
    script = REPO_ROOT / ".devcontainer/utils/setup-airflow-settings.sh"
    workspace = tmp_path / "workspace"
    (workspace / ".airflow").mkdir(parents=True)
    (workspace / "airflow_settings.yaml").write_text(
        """airflow:
  connections:
    - conn_id: 'databricks_default'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
    - conn_id: 'caspian-training-databricks'
      conn_type: 'databricks'
      conn_host: 'https://example.cloud.databricks.com'
      conn_login: ''
      conn_password: 'existing-token'
  pools: []
  variables:
    - variable_name: databricks_job_prefix
      variable_value: ""
""",
        encoding="utf-8",
    )

    home = tmp_path / "home"
    (home / ".config/dpc").mkdir(parents=True)
    (home / ".config/dpc/databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=pat\n"
        "export DATABRICKS_HOST=https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )
    (home / ".databrickscfg").write_text(
        "[DEFAULT]\n"
        "host = https://example.cloud.databricks.com\n"
        "token = dapi-test-pat-token\n",
        encoding="utf-8",
    )

    import subprocess

    result = subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    rendered = (workspace / "airflow_settings.yaml").read_text(encoding="utf-8")
    assert "conn_password: 'dapi-test-pat-token'" in rendered
    assert "conn_password: 'existing-token'" not in rendered


def test_dpc_check_oauth_health_includes_live_airflow_databricks_validation() -> None:
    script = _read(".devcontainer/check.sh")
    assert "OAuth Airflow databricks_default connection works" in script
    assert "airflow connections test databricks_default" in script
    assert "run_with_timeout" in script


def test_airflow_settings_runs_after_oauth_setup() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."setup:airflow-settings"]' in mise
    assert 'depends = ["setup:databricks"]' in mise
    assert mise.count('setup-airflow-settings.sh') == 1


def test_compose_uses_repo_relative_dag_mount() -> None:
    override = _read("docker-compose.override.yml")
    assert "./data_products:/usr/local/airflow/dags" in override
    assert "HOST_WORKSPACE_PATH" not in override


def test_compose_overrides_airflow3_api_server_not_webserver() -> None:
    override = _read("docker-compose.override.yml")
    assert "api-server:" in override
    assert "webserver:" not in override


def test_compose_disables_remote_logging_for_local_astro() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW__LOGGING__REMOTE_LOGGING: \"False\"" in override
    assert "AIRFLOW__ASTRO_SECONDARY_LOGS__S3_BUCKET_ENABLED: \"False\"" in override


def test_compose_uses_local_secrets_backend_for_local_astro() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW__SECRETS__BACKEND: \"airflow.secrets.metastore.MetastoreBackend\"" in override
    assert "AIRFLOW__SECRETS__BACKEND_KWARGS: \"{}\"" in override


def test_compose_override_uses_metastore_secrets_backend() -> None:
    compose = _read("docker-compose.override.yml")
    # MetastoreBackend is required so DB-stored connections resolve for hooks.
    assert "airflow.secrets.metastore.MetastoreBackend" in compose
    # The prior value dropped the metastore and broke DB connections.
    assert "environment_variables.EnvironmentVariablesBackend" not in compose


def test_compose_applies_local_overrides_to_db_migration() -> None:
    override = _read("docker-compose.override.yml")
    assert "db-migration:" in override
    assert "db-migration:\n    <<: *airflow-common" in override


def test_compose_applies_local_overrides_to_dag_processor() -> None:
    override = _read("docker-compose.override.yml")
    assert "dag-processor:" in override
    assert "dag-processor:\n    <<: *airflow-common" in override


def test_airflow_settings_template_uses_bearer_connection_shape() -> None:
    tmpl = _read(".airflow/airflow_settings.yaml.example")
    # Bearer requires an EMPTY login; a non-empty login forces HTTP Basic auth,
    # which an OAuth token rejects (verified: 401 via DatabricksHook).
    assert "conn_login: 'token'" not in tmpl
    assert "conn_login: ''" in tmpl


def test_airflow_settings_generator_writes_empty_login() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert "conn_login: 'token'" not in script
    assert "conn_login: ''" in script


def test_airflow_setup_starts_oauth_refresher_in_oauth_mode() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert "databricks-oauth-refresh.sh" in script
    assert "--loop" in script
    assert "nohup" in script
    assert 'DPC_DATABRICKS_AUTH_MODE:-}" = "oauth"' in script
    assert "DPC_SKIP_OAUTH_REFRESH" in script


def test_dpc_check_reports_airflow_runtime_recovery_hint() -> None:
    script = _read(".devcontainer/check.sh")
    assert 'soft_check "astro scheduler container running"' in script
    assert 'soft_check "astro api-server container running"' in script
    assert "astro dev start --wait 5m" in script


def test_compose_sets_local_airflow_variables_needed_by_dag_templates() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW_VAR_DEV_CLUSTER_ID" in override
    assert "AIRFLOW_VAR_ROOT_PATH" in override
    assert "AIRFLOW_VAR_DATA_PRODUCT_NAME" in override
    assert "AIRFLOW_VAR_DATABRICKS_JOB_PREFIX" in override
    assert "AIRFLOW_VAR_CGREGISTRY_HOST" in override
    assert "AIRFLOW_VAR_CGREGISTRY_IMAGE" in override


def test_compose_maps_databricks_connections_from_env() -> None:
    override = _read("docker-compose.override.yml")
    assert ".databrickscfg:/home/astro/.databrickscfg" in override
    assert "DATABRICKS_HOST" in override
    assert "DATABRICKS_HTTP_PATH" in override
    assert "DATABRICKS_CONFIG_FILE: /home/astro/.databrickscfg" in override


def test_all_dataset_dag_yaml_files_are_valid_yaml() -> None:
    import yaml

    for path in (REPO_ROOT / "data_products").rglob("**/airflow/*.dag.yml"):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_dataset_dag_yaml_files_have_unique_dag_ids() -> None:
    import yaml

    by_dag_id: dict[str, list[str]] = {}
    for path in (REPO_ROOT / "data_products").rglob("**/airflow/*.dag.yml"):
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        dag_id = config.get("dag_id")
        if dag_id:
            by_dag_id.setdefault(str(dag_id), []).append(str(path.relative_to(REPO_ROOT)))

    duplicates = {dag_id: paths for dag_id, paths in by_dag_id.items() if len(paths) > 1}
    assert not duplicates, f"Duplicate DAG IDs found: {duplicates}"
