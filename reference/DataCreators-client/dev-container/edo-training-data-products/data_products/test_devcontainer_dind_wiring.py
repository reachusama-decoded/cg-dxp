from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_json_permissive(text: str) -> dict:
    """Load JSON that may contain // line comments or /* */ block comments.
    This implements a simple comment stripper, not a full JSON5 parser —
    sufficient for the test files here.
    """
    # remove /* ... */ block comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # remove // line comments
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    # remove trailing commas before ] or }
    text = re.sub(r",\s*([\]\}])", r"\1", text)
    return json.loads(text)


def test_atlas_elt_has_required_product_shell() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt"
    required_paths = [
        "databricks.yml",
        "dbt_project.yml",
        "dbt_profiles/profiles.yml",
        "packages.yml",
        "requirements.txt",
        "dqf_requirements.txt",
        "DATABRICKS_RUNTIME_VERSION",
        ".dbtignore",
        ".copier-answers.yml",
        "variables/variables.yml",
        "variables/clusters.yml",
        "init_scripts/install_requirements.sh",
        "python/main.py",
        "shared/tests/.gitkeep",
        "datasets/sources.yml",
    ]
    for rel in required_paths:
        assert (root / rel).exists(), rel


def test_atlas_elt_has_all_atlas_entity_dataset_folders() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    for name in [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]:
        assert (root / name).is_dir(), name


def test_each_atlas_dataset_has_required_artifact_directories() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    required = ["airflow", "bundle", "contract", "dbt", "runtime"]
    for dataset in [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]:
        for child in required:
            assert (base / dataset / child).is_dir(), f"{dataset}/{child}"


def test_each_atlas_dataset_has_named_artifact_files() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    for dataset in [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]:
        expected_files = [
            f"airflow/{dataset}.dag.yml",
            f"bundle/{dataset}.job.yml",
            f"bundle/{dataset}_dq.job.yml",
            f"contract/{dataset}.odcs.yaml",
            "contract/migrations/.gitkeep",
            f"dbt/{dataset}.yml",
            "runtime/dq_verify.py",
            "cspn_migration.md",
        ]
        for rel in expected_files:
            assert (base / dataset / rel).is_file(), f"{dataset}/{rel}"
        assert list((base / dataset / "dbt" / "staging").glob("*.sql")), f"{dataset}/dbt/staging/*.sql"
        assert list((base / dataset / "dbt" / "integration").glob("*.sql")), f"{dataset}/dbt/integration/*.sql"


def test_atlas_elt_no_longer_uses_demo_dataset_names() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt"
    assert not (root / "datasets" / "demo").exists()
    text = (root / "dbt_project.yml").read_text(encoding="utf-8")
    assert "demo_values" not in text


def test_atlas_seed_resource_names_do_not_collide_with_models() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt"
    seed_names = {path.stem for path in (root / "seeds").glob("*.csv")}
    model_names = {path.stem for path in (root / "datasets").rglob("*.sql")}
    assert seed_names.isdisjoint(model_names)


def test_atlas_seed_rows_do_not_end_in_whitespace() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt" / "seeds"
    for path in root.glob("*.csv"):
        assert all(line == line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())


def test_atlas_model_yaml_names_match_sql_filenames() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    for path in root.glob("*/dbt/*.yml"):
        text = path.read_text(encoding="utf-8")
        dbt_dir = path.parent
        model_names = sorted(p.stem for p in dbt_dir.glob("**/*.sql"))
        for name in model_names:
            assert f"- name: {name}\n" in text, str(path.relative_to(root))


def test_atlas_dataset_artifacts_do_not_include_reference_data_content() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    for path in base.rglob("*"):
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            assert "currency" not in content.lower(), str(path.relative_to(base))
            assert "geography" not in content.lower(), str(path.relative_to(base))


def test_devcontainer_uses_dind_run_args() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    run_args = cfg.get("runArgs", [])
    mounts = cfg.get("mounts", [])
    # Require explicit dind flags and no docker socket mount when using dind wiring.
    has_flags = "--privileged" in run_args and "--init" in run_args
    no_sock_mount = not any("/var/run/docker.sock" in m for m in mounts)
    assert has_flags, "devcontainer runArgs must include --privileged and --init"
    assert no_sock_mount, "devcontainer must not mount /var/run/docker.sock when using dind wiring"


def test_post_start_command_uses_repo_script() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    post = cfg.get("postStartCommand", "")
    # Require the repo's post-start script to be used for postStartCommand
    assert "post-start.sh" in post, "postStartCommand must include post-start.sh"


def test_post_start_heals_dockerd_before_health_check() -> None:
    script = _read(".devcontainer/post-start.sh")
    assert "/usr/local/bin/start-dockerd.sh" in script
    assert "/usr/local/bin/ensure-dockerd.sh" in script
    assert "/usr/local/bin/dpc-check" in script


def test_fresh_clone_does_not_require_an_untracked_env_file_to_start() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    run_args = cfg.get("runArgs", [])
    assert "--env-file" not in run_args

    mise = _read(".mise.toml")
    assert "cp .devcontainer/utils/.env.example .devcontainer/.env" in mise
    assert '_.file = ".devcontainer/.env"' not in mise


def test_setup_task_points_to_oauth_script() -> None:
    mise = _read(".mise.toml")
    # Require the mise setup task to reference the repo oauth/setup script
    assert 'setup-databricks-dbt.sh' in mise, ".mise.toml must reference setup-databricks-dbt.sh"


def test_setup_script_exists_and_mise_references_it() -> None:
    script = REPO_ROOT / ".devcontainer" / "setup-databricks-dbt.sh"
    assert script.exists()
    assert "setup-databricks-dbt.sh" in _read(".mise.toml")


def test_setup_script_ignores_template_tokens() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "your-token-here" in script
    assert "replace-with-your-token" in script
    assert 'if is_placeholder_token "${DATABRICKS_TOKEN:-}"; then' in script
    assert 'FORCE_PAT_SETUP' in script
    assert '--pat' in script
    assert 'if [ -n "${DATABRICKS_TOKEN:-}" ]; then' not in script


def test_setup_script_keeps_real_training_defaults() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "DATABRICKS_HOST:https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com" not in script
    assert "DATABRICKS_HTTP_PATH:/sql/1.0/warehouses/267dd55b7f7395ce" not in script
    assert "read_required" in script
    assert "Databricks workspace URL" in script


def test_host_prompt_defaults_to_training_workspace_for_pat_and_oauth() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'DEFAULT_TRAINING_DATABRICKS_HOST="https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com"' in script
    assert script.count('read_required DATABRICKS_HOST "Databricks workspace URL (e.g. https://cg-db-...cloud.databricks.com)" "$DEFAULT_TRAINING_DATABRICKS_HOST"') == 2


def test_pat_setup_prompts_for_missing_values() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'if [ "$use_pat_setup" -eq 1 ]; then' in script
    assert 'read_required DATABRICKS_HOST "Databricks workspace URL' in script
    assert "pick_warehouse || read_required DATABRICKS_HTTP_PATH" in script
    assert 'read_secret_required DATABRICKS_TOKEN "Databricks PAT token"' in script
    assert "Databricks PAT setup requires DATABRICKS_HOST" not in script


def test_pat_setup_validates_token_before_writing_config() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert 'if [ -z "${DATABRICKS_BIN:-}" ] || [ ! -x "$DATABRICKS_BIN" ]; then' in script
    assert "_resolve_databricks_bin()" in script
    assert 'find "$HOME/.local/share/mise/installs/databricks-cli"' in script
    assert 'DATABRICKS_BIN=$(_resolve_databricks_bin)' in script
    assert 'DATABRICKS_AUTH_TYPE=pat' not in script
    assert 'curl -sS -o /tmp/databricks-pat-validate.json -w "%{http_code}"' in script
    assert 'Authorization: Bearer $DATABRICKS_TOKEN' in script
    assert '$DATABRICKS_HOST/api/2.0/preview/scim/v2/Me' in script
    assert "Databricks PAT token authentication failed" in script
    assert "PAT validation details:" in script
    assert 'Set DATABRICKS_TOKEN to a valid PAT and rerun setup with --pat.' in script
    assert '"${DATABRICKS_BIN:-databricks}" warehouses list --output json' in script
    assert "if ! validate_pat_token; then" in script
    assert 'read_secret_required DATABRICKS_TOKEN "Databricks PAT token (retry)"' in script


def test_pat_setup_prompts_token_before_warehouse_pick() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    token_prompt = script.index('read_secret_required DATABRICKS_TOKEN "Databricks PAT token"')
    warehouse_pick = script.index('pick_warehouse || read_required DATABRICKS_HTTP_PATH')
    assert token_prompt < warehouse_pick


def test_setup_script_handles_oauth_callback_port_collisions() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "clear_oauth_callback_port" in script
    assert "ss -ltnp" in script
    assert "databricks auth login" in script


def test_setup_script_handles_databrickscfg_directory_collision() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    assert "ensure_databrickscfg_path" in script
    assert "exists as a directory, but Databricks CLI requires it to be a file." in script
    assert "rmdir \"$databrickscfg\"" in script


def test_oauth_tokens_are_refreshed_without_disk_persistence() -> None:
    setup = _read(".devcontainer/setup-databricks-dbt.sh")
    mise_env = _read(".mise/env.sh")

    assert "export DPC_DATABRICKS_AUTH_MODE=oauth" in setup
    assert "export DATABRICKS_AUTH_TYPE=" not in setup
    assert "export DBT_ACCESS_TOKEN=" not in setup
    assert "export DATABRICKS_TOKEN=" not in setup
    assert "databricks auth token" not in setup
    assert 'if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then' in mise_env
    assert "auth token --profile DEFAULT" in mise_env


def test_oauth_shell_refresh_does_not_export_databricks_token_env() -> None:
    mise_env = _read(".mise/env.sh")
    assert 'export DBT_ACCESS_TOKEN="$_oauth_token"' in mise_env
    assert 'export DATABRICKS_TOKEN="$_oauth_token"' not in mise_env


def test_oauth_refresher_forces_refresh_on_scheduler_reappearance() -> None:
    script = _read(".devcontainer/utils/databricks-oauth-refresh.sh")
    assert "last_scheduler" in script
    assert "scheduler_changed" in script
    # The refresher must inspect container identity (ID) so recreation is detected
    assert "docker ps --format '{{.ID}} {{.Names}}'" in script or "docker ps --format '{{.ID}}'" in script
    assert "sleep_s=1" in script or "sleep_s=0" in script


def test_oauth_refresher_checks_scheduler_while_waiting() -> None:
    script = _read(".devcontainer/utils/databricks-oauth-refresh.sh")
    # Long sleeps should be chunked so the refresher can detect scheduler changes while waiting.
    assert "remaining=$sleep_s" in script
    assert 'while [ "$remaining" -gt 0 ]' in script
    assert 'sleep "$chunk"' in script
    assert "resolve_scheduler" in script
    assert "breaking early to refresh" in script or "scheduler identity changed during wait" in script


def test_oauth_refresher_reports_retryable_failure_when_connection_upsert_fails(tmp_path) -> None:
    home = tmp_path / "home"
    config_dir = home / ".config" / "dpc"
    config_dir.mkdir(parents=True)
    (config_dir / "databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://example.cloud.databricks.com\n",
        encoding="utf-8",
    )

    import os
    import subprocess

    result = subprocess.run(
        [
            "bash",
            "-c",
            f'''
source "{(REPO_ROOT / REFRESHER).as_posix()}" --source-only
resolve_scheduler() {{ printf '%s\\n' fake-scheduler; }}
mint_payload() {{
  printf '%s\\n' '{{"access_token":"token","expiry":"2030-01-01T00:00:00Z"}}'
}}
upsert_connection() {{
  if [ "$2" = "databricks_default" ]; then
    return 1
  fi
  return 0
}}
refresh_once
printf 'rc=%s\\n' "$?"
''',
        ],
        cwd=home,
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "rc=2" in result.stdout
    status = json.loads((config_dir / "oauth-refresh-status.json").read_text(encoding="utf-8"))
    assert status["state"] == "connection_update_failed"
    assert status["token_expiry"] == ""


def test_mise_env_avoids_databricks_shim_recursion() -> None:
    mise_env = _read(".mise/env.sh")
    assert "_resolve_databricks_bin()" in mise_env
    assert "/shims/databricks" in mise_env
    assert "installs/databricks-cli" in mise_env
    assert 'timeout 10 "$_databricks_bin" auth token' in mise_env


def test_airflow_setup_tolerates_a_missing_template() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert 'if [ ! -f "$EXAMPLE_FILE" ]; then' in script
    assert "Airflow settings template not found" in script


def test_setup_wires_databricks_http_path_to_dbt() -> None:
    for path in (
        ".devcontainer/setup-databricks-dbt.sh",
        ".devcontainer/utils/setup-databricks-config.sh",
        ".devcontainer/utils/normalize-env.sh",
    ):
        assert "DBT_HTTP_PATH" in _read(path), f"{path} must export DBT_HTTP_PATH"


def test_setup_contract_exports_databricks_catalog_and_schema() -> None:
    for path in (
        ".devcontainer/setup-databricks-dbt.sh",
        ".devcontainer/utils/setup-databricks-config.sh",
    ):
        content = _read(path)
        assert "DATABRICKS_CATALOG" in content, f"{path} must export DATABRICKS_CATALOG"
        assert "DATABRICKS_SCHEMA" in content, f"{path} must export DATABRICKS_SCHEMA"
        assert "AIRFLOW_VAR_DATABRICKS_JOB_PREFIX" in content, (
            f"{path} must export AIRFLOW_VAR_DATABRICKS_JOB_PREFIX for local Airflow job-name templating"
        )


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


def test_dpc_check_oauth_health_includes_live_airflow_databricks_validation() -> None:
    script = _read(".devcontainer/check.sh")
    assert "OAuth Airflow databricks_default connection works" in script
    assert "airflow connections test databricks_default" in script
    assert "run_with_timeout" in script


def test_dockerd_lifecycle_serializes_start_and_heals_async() -> None:
    start = _read(".devcontainer/start-dockerd.sh")
    ensure = _read(".devcontainer/ensure-dockerd.sh")

    assert "dockerd-start.lock" in start
    assert "mkdir \"$lock_dir\"" in start
    assert "ps -ef | awk '$0 ~ /[ /](dockerd|containerd)([ ]|$)/ {print $2}'" not in start
    assert "grep -E '[ /](dockerd|containerd)([ ]|$)'" in start
    assert "--no-wait" in start
    assert "nohup /usr/local/bin/start-dockerd.sh --restart --no-wait" in ensure
    assert "DPC_SKIP_DOCKERD_HEAL" in ensure
    assert "pgrep -x dockerd" in ensure
    assert "for pid in" not in ensure


def test_interactive_shell_triggers_dockerd_heal() -> None:
    bashrc = _read(".devcontainer/utils/bashrc")
    assert "/usr/local/bin/ensure-dockerd.sh" in bashrc


def test_post_start_sanitizes_devcontainer_docker_credstore() -> None:
    post_start = _read(".devcontainer/post-start.sh")
    assert "credsStore" in post_start
    assert "dev-containers-" in post_start
    assert "jq 'del(.credsStore)'" in post_start


def test_devcontainer_forwards_oauth_and_airflow_ports() -> None:
    cfg = _load_json_permissive(_read(".devcontainer/devcontainer.json"))
    ports = cfg.get("forwardPorts", [])
    assert 8020 in ports
    assert 8080 in ports
    assert 6563 in ports


def test_troubleshooting_uses_inner_docker_daemon() -> None:
    guide = _read(".devcontainer/TROUBLESHOOTING.md")
    assert "/var/run/docker.sock" not in guide
    assert "/usr/local/bin/ensure-dockerd.sh" in guide


def test_integration_marker_is_registered() -> None:
    pytest_ini = _read("pytest.ini")
    assert "markers =" in pytest_ini
    assert "integration:" in pytest_ini


def test_airflow_settings_runs_after_oauth_setup() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."setup:airflow-settings"]' in mise
    assert 'depends = ["setup:databricks-oauth"]' in mise
    assert mise.count('setup-airflow-settings.sh') == 1


def test_mise_excludes_deprecated_setup_tasks() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."setup:host-path"]' not in mise
    assert '[tasks."setup:normalize-env"]' not in mise
    assert '[tasks."setup:databricks"]' not in mise


def test_oauth_setup_no_longer_requires_env_bootstrap() -> None:
    mise = _read(".mise.toml")
    block = mise.split('[tasks."setup:databricks-oauth"]', 1)[1].split("[tasks.", 1)[0]
    assert "depends =" not in block


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


def test_compose_disables_datadog_for_local_astro() -> None:
    override = _read("docker-compose.override.yml")
    assert "ASTRO_DATADOG_TASK_LOGS_ENABLED: \"false\"" in override
    assert "AIRFLOW__METRICS__STATSD_DATADOG_ENABLED: \"false\"" in override


def test_compose_uses_local_secrets_backend_for_local_astro() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW__SECRETS__BACKEND: \"airflow.secrets.metastore.MetastoreBackend\"" in override
    assert "AIRFLOW__SECRETS__BACKEND_KWARGS: \"{}\"" in override


def test_compose_uses_db_xcom_backend_for_local_astro() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW__CORE__XCOM_BACKEND: \"airflow.sdk.execution_time.xcom.BaseXCom\"" in override


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


def test_full_setup_does_not_block_on_interactive_oauth() -> None:
    mise = _read(".mise.toml")
    assert '[tasks.setup]' in mise
    assert "setup:databricks-oauth" not in mise.split('[tasks.setup]')[-1].split('[tasks.', 1)[0]


def test_astro_onbuild_is_forced_to_pip_mode() -> None:
    req = _read("requirements.txt")
    assert "ASTRO_RUNTIME_USE_PIP" in req


def test_astro_requirements_include_corp_trusted_hosts() -> None:
    req = _read("requirements.txt")
    assert "--trusted-host pip.astronomer.io" in req
    assert "--trusted-host pypi.org" in req
    assert "--trusted-host files.pythonhosted.org" in req


def test_requirements_pypi_pins_airflow_provider_stack_for_stable_resolution() -> None:
    req = _read("requirements-pypi.txt")
    # Avoid provider-extra backtracking blowups: keep one amazon provider entry and pin
    # the known-good dependency set used by local Astro builds.
    assert "apache-airflow-providers-amazon[s3fs]" not in req
    assert "apache-airflow-providers-amazon==9.16.0" in req
    assert "apache-airflow-providers-databricks==7.7.4" in req
    assert "apache-airflow-providers-datadog==3.9.2" in req
    assert "apache-airflow-providers-cncf-kubernetes==10.19.0" in req
    assert "apache-airflow-providers-http==5.4.0" in req
    assert "apache-airflow-providers-fab==3.0.1" in req
    assert "s3fs==2025.10.0" in req
    assert "fsspec==2025.10.0" in req
    assert "pandas==2.1.4" in req
    assert "pyarrow==18.1.0" in req
    assert "numpy==1.26.4" in req


def test_dockerfile_uses_buildkit_cache_mounts_for_apt_and_pip() -> None:
    dockerfile = _read("Dockerfile")
    assert "--mount=type=cache,target=/var/cache/apt" in dockerfile
    assert "--mount=type=cache,target=/var/lib/apt/lists" in dockerfile
    assert "--mount=type=cache,target=/root/.cache/pip" in dockerfile
    assert "--mount=type=cache,target=/home/astro/.cache/pip" in dockerfile


def test_dockerfile_uses_fix_container_certs_frontend() -> None:
    first_line = _read("Dockerfile").splitlines()[0].strip()
    assert first_line == "#syntax=cgregistry.capgroup.com/fix-container-certs:1.9"


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


def test_compose_sets_local_airflow_variables_needed_by_dag_templates() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW_VAR_DEV_CLUSTER_ID" in override
    assert "AIRFLOW_VAR_ROOT_PATH" in override
    assert "AIRFLOW_VAR_DATA_PRODUCT_NAME" in override
    assert "AIRFLOW_VAR_DATABRICKS_JOB_PREFIX" in override
    assert "AIRFLOW_VAR_DATA_NOTIFY_TOPIC" in override
    assert "AIRFLOW_VAR_KAFKA_SECRET_SCOPE" in override
    assert "AIRFLOW_VAR_BOOTSTRAP_BROKERS" in override
    assert "AIRFLOW_VAR_SCHEMA_REGISTRY_URL" in override
    assert "AIRFLOW_VAR_AWS_REGION" in override
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


def test_setup_python_deps_installs_sitecustomize_into_venv() -> None:
    script = _read(".devcontainer/utils/setup-python-deps.sh")
    assert ".devcontainer/sitecustomize.py" in script
    assert "sitecustomize.py" in script
    assert ".venv/bin/python" in script
    assert "/opt/venv/bin/python" in script
    assert "certifi.where()" in script


def test_repo_includes_atlas_data_product() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt"
    assert (root / "dbt_project.yml").is_file()
    assert (root / "dbt_profiles" / "profiles.yml").is_file()
    for entity in [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]:
        assert (root / "seeds" / f"{entity}.csv").is_file()


def test_atlas_elt_uses_refinement_layer_model_names() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt" / "datasets"
    entities = [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]
    for entity in entities:
        staging = [p.stem for p in (base / entity / "dbt" / "staging").glob("*.sql")]
        integration = [p.stem for p in (base / entity / "dbt" / "integration").glob("*.sql")]
        assert staging and any(name.startswith("src_") for name in staging), entity
        assert integration and any(name.startswith(("dom_", "rpt_")) for name in integration), entity
        assert not any(name.startswith(("bronze_", "silver_", "gold_")) for name in staging + integration), entity


def test_atlas_elt_run_selector_executes_source_to_domain_chain() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt" / "datasets" / "trades" / "dbt"
    src = root / "staging" / "src_trading__trades.sql"
    dom_stub = root / "integration" / "dom_trading__trade.sql"
    solved_dom = (
        REPO_ROOT
        / "challenges"
        / "04-atlas-capstone"
        / "solution"
        / "datasets"
        / "trades"
        / "dbt"
        / "integration"
        / "dom_trading__trade.sql"
    )

    assert src.is_file()
    assert dom_stub.is_file()
    assert solved_dom.is_file()
    assert "select 1 as placeholder" in dom_stub.read_text(encoding="utf-8")
    assert "ref('src_trading__trades')" in solved_dom.read_text(encoding="utf-8")


def test_atlas_elt_no_staging_wildcard_selector_dependency() -> None:
    spec = _read("data_products/atlas_elt/datasets/trades/bundle/trades.job.yml")

    assert "+src_trading__trades+" in spec
    assert "+staging_*" not in spec


def test_atlas_dqf_cluster_is_job_cluster_compatible() -> None:
    clusters = _read("data_products/atlas_elt/variables/clusters.yml")
    assert "spark.databricks.cluster.profile: \"singleNode\"" in clusters
    assert "cluster_log_conf:" not in clusters


def test_validate_pat_token_has_no_unreachable_duplicate_block() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    # The Me-probe curl must appear exactly once inside validate_pat_token.
    assert script.count('/api/2.0/preview/scim/v2/Me') == 1
    # No code after the function's successful 'return 0' before the closing brace.
    func = script.split("validate_pat_token() {", 1)[1].split("\n}", 1)[0]
    lines_after_return = func.split("return 0", 1)[1].strip()
    assert lines_after_return == "", (
        "validate_pat_token has unreachable code after 'return 0':\n" + lines_after_return
    )


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


import os as _os_refresher
import subprocess as _sp_refresher

REFRESHER = ".devcontainer/utils/databricks-oauth-refresh.sh"


def test_oauth_refresher_exists_and_is_executable() -> None:
    path = REPO_ROOT / REFRESHER
    assert path.exists(), "refresher script missing"
    assert _os_refresher.access(path, _os_refresher.X_OK), "refresher script must be executable"


def test_oauth_refresher_core_contract() -> None:
    script = _read(REFRESHER)
    # Mode gate: no-op unless oauth.
    assert 'if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then' in script
    # Browser-free minting only.
    assert "databricks auth token" in script
    assert "databricks auth login" not in script
    # Scheduler discovery by dynamic-hash pattern.
    assert "^edo-training.*-scheduler-1$" in script
    # Upserts BOTH connection ids via the Airflow CLI.
    assert "databricks_default" in script
    assert "caspian-training-databricks" in script
    assert "airflow connections add" in script
    assert "airflow connections delete" in script
    # Heartbeat + log destinations from the design.
    assert "oauth-refresh-status.json" in script
    assert "/var/log/dbx-oauth-refresh.log" in script
    # Bearer connection shape: empty login (NOT login: token).
    assert '"login": ""' in script
    assert '"login": "token"' not in script


def test_oauth_refresher_is_noop_when_mode_is_pat(tmp_path) -> None:
    home = tmp_path
    cfg_dir = home / ".config" / "dpc"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "databricks.env").write_text("export DPC_DATABRICKS_AUTH_MODE=pat\n")
    # Normal PATH so bash/coreutils resolve; the no-op guarantee comes from the
    # mode gate returning before any docker/databricks call, not PATH starvation.
    env = {"HOME": str(home), "PATH": _os_refresher.environ.get("PATH", "")}
    result = _sp_refresher.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--once"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_oauth_refresher_loop_contract() -> None:
    script = _read(REFRESHER)
    assert "--loop" in script
    assert "DPC_SKIP_OAUTH_REFRESH" in script
    assert "oauth-refresh.pid" in script
    assert "kill -0" in script
    assert "seconds_until_refresh" in script
    assert "3300" in script
    assert "120" in script


def test_oauth_refresher_loop_opts_out_immediately(tmp_path) -> None:
    home = tmp_path
    (home / ".config" / "dpc").mkdir(parents=True)
    (home / ".config" / "dpc" / "databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
    )
    env = {
        "HOME": str(home),
        "PATH": _os_refresher.environ.get("PATH", ""),
        "DPC_SKIP_OAUTH_REFRESH": "1",
    }
    result = _sp_refresher.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--loop"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_seconds_until_refresh_helper(tmp_path) -> None:
    probe = (
        f'source "{REPO_ROOT / REFRESHER}" --source-only 2>/dev/null; '
        'seconds_until_refresh ""; '
        'echo "---"; '
        'seconds_until_refresh "not-a-date"'
    )
    result = _sp_refresher.run(
        ["bash", "-c", probe],
        env={"HOME": str(tmp_path), "PATH": _os_refresher.environ.get("PATH", "")},
        capture_output=True, text=True, timeout=30,
    )
    out = [line for line in result.stdout.splitlines() if line.strip()]
    assert out[0] == "3300"
    assert out[-1] == "3300"


def test_airflow_setup_starts_oauth_refresher_in_oauth_mode() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert "databricks-oauth-refresh.sh" in script
    assert "--loop" in script
    assert "nohup" in script
    assert 'DPC_DATABRICKS_AUTH_MODE:-}" = "oauth"' in script
    assert "DPC_SKIP_OAUTH_REFRESH" in script


def test_mise_has_oauth_refresh_task() -> None:
    toml = _read(".mise.toml")
    assert '[tasks."databricks:oauth-refresh"]' in toml
    assert "databricks-oauth-refresh.sh" in toml


def test_dpc_check_reports_auth_mode_and_refresher_health() -> None:
    script = _read(".devcontainer/check.sh")
    assert "DPC_DATABRICKS_AUTH_MODE" in script
    assert "oauth-refresh-status.json" in script
    assert "setup:databricks-oauth" in script or "setup-databricks-dbt.sh" in script
    assert "--pat" in script


def test_dpc_check_reports_airflow_runtime_recovery_hint() -> None:
    script = _read(".devcontainer/check.sh")
    assert 'soft_check "astro scheduler container running"' in script
    assert 'soft_check "astro api-server container running"' in script
    assert "astro dev start --wait 5m" in script


def test_dpc_check_refresher_health_is_read_only() -> None:
    script = _read(".devcontainer/check.sh")
    region = script.split("oauth-refresh-status.json", 1)[1][:400]
    assert "databricks " not in region, "heartbeat check must be read-only (no CLI call)"


def test_readme_documents_single_mode_auth_and_refresher() -> None:
    readme = _read(".devcontainer/README.md")
    assert "DPC_DATABRICKS_AUTH_MODE" in readme
    assert "OAuth" in readme and "PAT" in readme
    assert "databricks-oauth-refresh.sh" in readme or "token refresher" in readme
    assert "setup:databricks-oauth" in readme or "setup-databricks-dbt.sh" in readme
