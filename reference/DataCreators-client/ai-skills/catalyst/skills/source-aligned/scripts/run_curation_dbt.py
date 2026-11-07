#!/usr/bin/env python3
"""Run curation dbt models against Databricks, mirroring ig-accelerators-poc behavior."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import re
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def patch_dbt_content(content: str, target_name: str) -> str:
    content = content.replace("{{target.name}}", f"{target_name}")
    content = content.replace("chronological", "latest")
    content = content.replace('"vacuum {{ this }} retain 0 hours",', "")
    content = content.replace("vacuum {{ this }} retain 0 hours;", "")
    content = content.replace('"{{ cspn_commit_checkpoints() }}"', "")
    content = re.sub(
        r'schema\s*=\s*"cspn_work2_"\s*\|\s*string\s*\+\s*target\.name',
        "schema = env_var('DATABRICKS_DEFAULT_SCHEMA')",
        content,
    )
    content = re.sub(
        r'schema\s*=\s*"cspn_fndn2_"\s*\|\s*string\s*\+\s*target\.name',
        "schema = env_var('DATABRICKS_DEFAULT_SCHEMA')",
        content,
    )
    content = re.sub(
        r"\{%-?\s*set\s+source_schema_suffix.*?%\}\s*\{%-?\s*set\s+source_schema\s*=\s*'cspn_std_.*?%\}",
        "{% set source_schema = env_var('DATABRICKS_DEFAULT_SCHEMA') %}",
        content,
        flags=re.DOTALL,
    )
    if "generate_surrogate_key_v3()" in content:
        cols = None
        surrogate_match = re.search(r"surrogate_key_cols[\"']?\s*:\s*\[(.*?)\]", content, re.DOTALL)
        if surrogate_match:
            cols = surrogate_match.group(1).strip()
        elif "id_bb_unique" in content:
            cols = "'id_bb_unique'"
        if cols:
            content = content.replace("generate_surrogate_key_v3()", f"generate_surrogate_key_v3([{cols}])")
    return content


def copy_and_patch_models(source_models_dir: Path, target_models_dir: Path, target_name: str) -> None:
    if target_models_dir.exists():
        shutil.rmtree(target_models_dir)
    target_models_dir.mkdir(parents=True, exist_ok=True)

    for src in source_models_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(source_models_dir)
        dst = target_models_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in {".sql", ".yml", ".yaml"}:
            content = src.read_text(encoding="utf-8")
            content = patch_dbt_content(content, target_name)
            dst.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(src, dst)


def copy_tests_if_present(source_models_dir: Path, project_path: Path) -> None:
    tests_dir = source_models_dir.parent / "tests"
    if not tests_dir.exists():
        return
    target_tests_dir = project_path / "tests"
    target_tests_dir.mkdir(parents=True, exist_ok=True)
    for src in tests_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(tests_dir)
        dst = target_tests_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def run_cmd(cmd: List[str], env: dict) -> None:
    result = subprocess.run(cmd, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {' '.join(cmd)}
STDOUT:
{result.stdout}
STDERR:
{result.stderr}"
        )
    print(result.stdout)


def find_latest_models_dir(repo_root: Path, model_name: Optional[str]) -> Path:
    candidates: List[Tuple[float, Path]] = []
    for base in [repo_root / "workspace" / "generated"]:
        if not base.exists():
            continue
        coi_root = base / "source-aligned"
        if not coi_root.exists():
            continue
        if model_name:
            # Check curation-databricks/models first (preferred), then curation-emr/models, then models
            for subdir in ["curation-databricks/models", "curation-emr/models", "models"]:
                model_dir = coi_root / model_name / subdir
                if model_dir.exists():
                    candidates.append((model_dir.stat().st_mtime, model_dir))
                    break
            continue
        # Search for models in all possible locations
        for model_dir in coi_root.glob("*/curation-databricks/models"):
            if model_dir.exists():
                candidates.append((model_dir.stat().st_mtime, model_dir))
        for model_dir in coi_root.glob("*/curation-emr/models"):
            if model_dir.exists():
                candidates.append((model_dir.stat().st_mtime, model_dir))
        for model_dir in coi_root.glob("*/models"):
            if model_dir.exists() and "curation" not in str(model_dir):
                candidates.append((model_dir.stat().st_mtime, model_dir))
    if not candidates:
        raise FileNotFoundError("No generated models found under workspace/generated/source-aligned")
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def find_latest_dbt_project(repo_root: Path) -> Path:
    candidates: List[Tuple[float, Path]] = []
    for base in [repo_root / "workspace" / "generated"]:
        if not base.exists():
            continue
        for dbt_project in base.rglob("dbt_project.yml"):
            candidates.append((dbt_project.stat().st_mtime, dbt_project.parent))
    if not candidates:
        raise FileNotFoundError("No dbt_project.yml found under workspace/generated")
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def ensure_dbt_project(project_path: Path, profile_name: str = "coi_generated") -> None:
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "models").mkdir(parents=True, exist_ok=True)
    macros_dir = project_path / "macros_overrides"
    macros_dir.mkdir(parents=True, exist_ok=True)

    dbt_project_yml = project_path / "dbt_project.yml"
    if not dbt_project_yml.exists():
        dbt_project_yml.write_text(
            """
name: coi_generated
version: '1.0.0'
config-version: 2

profile: coi_generated

macro-paths:
    - macros_overrides

model-paths:
    - models

test-paths:
    - tests
""".lstrip(),
            encoding="utf-8",
        )

    profiles_yml = project_path / "profiles.yml"
    if not profiles_yml.exists():
        profiles_yml.write_text(
            f"""
{profile_name}:
    target: "{{{{ env_var('DBT_TARGET', 'dev1') }}}}"
    outputs:
        dev1:
            type: databricks
            host: "{{{{ env_var('DATABRICKS_HOST') }}}}"
            http_path: "{{{{ env_var('DATABRICKS_HTTP_PATH') }}}}"
            token: "{{{{ env_var('DATABRICKS_TOKEN') }}}}"
            catalog: "{{{{ env_var('DATABRICKS_DEFAULT_CATALOG', '') }}}}"
            schema: "{{{{ env_var('DATABRICKS_DEFAULT_SCHEMA', '') }}}}"
            threads: 4
""".lstrip(),
            encoding="utf-8",
        )

    macros_file = macros_dir / "cspn_utils.sql"
    if not macros_file.exists():
        macros_file.write_text(
            """
{% macro cspn_source(source_schema, table_name) -%}
    {%- set catalog = (target.catalog if target.catalog is defined and target.catalog else target.database) -%}
    {{ catalog }}.{{ source_schema }}.{{ table_name }}
{%- endmacro %}

{% macro cspn_commit_checkpoints() -%}
    {{ return('') }}
{%- endmacro %}
""".lstrip(),
            encoding="utf-8",
        )


def copy_coi_macro_overrides(repo_root: Path, project_path: Path) -> None:
    templates_dir = repo_root / "plugins" / "casper" / "skills" / "source-aligned" / "templates" / "dbt_project" / "macros_overrides"
    if not templates_dir.exists():
        return
    target_dir = project_path / "macros_overrides"
    target_dir.mkdir(parents=True, exist_ok=True)
    for src in templates_dir.iterdir():
        if src.is_file():
            (target_dir / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def ensure_macro_overrides(project_path: Path) -> None:
    macros_dir = project_path / "macros_overrides"
    macros_dir.mkdir(parents=True, exist_ok=True)

    surrogate_macro = macros_dir / "surrogate_key_v3.sql"
    surrogate_macro.write_text(
        """
{% macro generated__surrogate_key_expr(cols) -%}
    sha2(
        concat_ws(
            '|'
            {%- for c in cols %}
            , coalesce(cast({{ c }} as string), '')
            {%- endfor %}
        ),
        256
    )
{%- endmacro %}

{% macro generate_surrogate_key_v3(cols=None) -%}
    {% if cols is none %}
        {% set meta = (model.config.meta if model is defined and model.config is defined and model.config.meta is defined else None) %}
        {% if not meta %}
            {% set meta = (model.meta if model is defined and model.meta is defined else {}) %}
        {% endif %}
        {% set cols = meta.get('surrogate_key_cols', []) %}
    {% endif %}
    {% if cols is string %}{% set cols = [cols] %}{% endif %}
    {% if cols is none or (cols | length) == 0 %}
        {% set model_name = (model.name if model is defined and model.name is defined else this.identifier) %}
        {% if model_name in ['equity_namr_v4','equity_namr_cins_v4'] %}
            {% set cols = ['id_bb_unique'] %}
        {% else %}
            {{ exceptions.raise_compiler_error('Missing surrogate key columns; expected `meta.surrogate_key_cols`') }}
        {% endif %}
    {% endif %}
    {{ generated__surrogate_key_expr(cols) }} as dl_row_uid
{%- endmacro %}

{% macro get_audit_cols() -%}
    cast('{{ var('run_id', invocation_id) }}' as string) as dl_last_update_process_id,
    'Y' as dl_current_indicator,
    to_date('1900-01-01') as dl_business_start_date,
    to_date('9999-12-31') as dl_business_end_date,
    cast(current_timestamp() as timestamp) as dl_system_start_timestamp,
    cast('9999-12-31 23:59:59' as timestamp) as dl_system_end_timestamp
{%- endmacro %}
""".lstrip(),
        encoding="utf-8",
    )

    create_schema_macro = macros_dir / "create_schema.sql"
    create_schema_macro.write_text(
        """
{% macro create_schema(relation) -%}
    {{ return('') }}
{%- endmacro %}
""".lstrip(),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run curation dbt models on Databricks")
    parser.add_argument("--dbt-project", help="Path to dbt project root (auto-detected if omitted)")
    parser.add_argument("--models-dir", help="Path to generated models directory (auto-detected if omitted)")
    parser.add_argument("--model-name", help="Model name under workspace/generated/source-aligned")
    parser.add_argument("--profiles-dir", help="Path to dbt profiles dir (default: project root)")
    parser.add_argument("--target", help="dbt target name (default: DBT_TARGET or dev1)")
    parser.add_argument("--select", action="append", help="dbt --select pattern (repeatable)")
    parser.add_argument("--vars", help="JSON string for dbt --vars")
    parser.add_argument("--full-refresh", action="store_true", help="Run dbt with --full-refresh")
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    load_dotenv(repo_root / ".env")

    if not os.environ.get("DATABRICKS_HTTP_PATH") and os.environ.get("DATABRICKS_WAREHOUSE_ID"):
        os.environ["DATABRICKS_HTTP_PATH"] = f"/sql/1.0/warehouses/{os.environ['DATABRICKS_WAREHOUSE_ID']}"

    if args.dbt_project:
        project_path = Path(args.dbt_project).resolve()
    else:
        try:
            project_path = find_latest_dbt_project(repo_root)
        except FileNotFoundError:
            project_path = repo_root / "workspace" / "generated" / "dbt_project"
            ensure_dbt_project(project_path)
    models_dir = (
        Path(args.models_dir).resolve()
        if args.models_dir
        else find_latest_models_dir(repo_root, args.model_name)
    )
    if not project_path.exists():
        raise FileNotFoundError(f"dbt project not found: {project_path}")
    if not models_dir.exists():
        raise FileNotFoundError(f"models dir not found: {models_dir}")

    profiles_dir = Path(args.profiles_dir).resolve() if args.profiles_dir else project_path
    target = args.target or os.environ.get("DBT_TARGET") or "dev1"

    required_env = ["DATABRICKS_HOST", "DATABRICKS_TOKEN"]
    missing = [k for k in required_env if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    copy_coi_macro_overrides(repo_root, project_path)

    copy_and_patch_models(models_dir, project_path / "models", target)
    copy_tests_if_present(models_dir, project_path)

    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = str(profiles_dir)
    env["DBT_TARGET"] = target

    dbt_cmd = [sys.executable, "-m", "dbt.cli.main"]
    packages_yml = project_path / "packages.yml"
    if packages_yml.exists():
        has_packages = any(
            line.strip().startswith("-")
            for line in packages_yml.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
        if has_packages:
            run_cmd(dbt_cmd + ["deps", "--project-dir", str(project_path)], env)

    cmd = dbt_cmd + ["run", "--project-dir", str(project_path), "--target", target, "--no-partial-parse"]
    if args.full_refresh:
        cmd.append("--full-refresh")
    if args.select:
        for sel in args.select:
            cmd += ["--select", sel]

    default_vars = {
        "source_schema_suffix": target,
    }
    if args.vars:
        try:
            user_vars = json.loads(args.vars)
        except json.JSONDecodeError as exc:
            raise ValueError("--vars must be valid JSON") from exc
        if not isinstance(user_vars, dict):
            raise ValueError("--vars must be a JSON object")
        merged_vars = {**default_vars, **user_vars}
        cmd += ["--vars", json.dumps(merged_vars)]
    else:
        cmd += ["--vars", json.dumps(default_vars)]

    run_cmd(cmd, env)


if __name__ == "__main__":
    main()
