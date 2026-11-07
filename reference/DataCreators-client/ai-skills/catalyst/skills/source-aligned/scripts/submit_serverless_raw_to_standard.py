#!/usr/bin/env python3
"""Submit serverless raw->standard jobs using Databricks SDK."""
from __future__ import annotations

import os
from pathlib import Path

import argparse

from databricks.sdk import WorkspaceClient

import yaml
from databricks.sdk.service import compute, jobs


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


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def upload_to_landing(
    client: WorkspaceClient,
    catalog: str,
    schema: str,
    ingestion_path: Path,
    input_file: Path,
) -> str:
    cfg = load_yaml(ingestion_path)
    l2r = cfg.get("l2r", {}) or {}
    landing_path = str(l2r.get("landing_path", "")).strip("/")
    if not landing_path:
        raise ValueError(f"Missing l2r.landing_path in {ingestion_path}")
    landing_base = os.environ.get("COI_DBX_LANDING_BASE") or f"/Volumes/{catalog}/{schema}/landing"
    dest = f"{landing_base}/{landing_path}/{input_file.name}"
    with input_file.open("rb") as f:
        client.files.upload(file_path=dest, contents=f, overwrite=True)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit serverless raw->standard jobs")
    parser.add_argument("--wait", action="store_true", help="Wait for run completion")
    parser.add_argument("--run-as-user", help="Run job as this user (email)")
    parser.add_argument("--volume", default="code", help="Volume name where code/configs are stored")
    parser.add_argument("--ingestion-yml", action="append", required=True, help="Ingestion YAML in volume")
    parser.add_argument(
        "--local-ingestion-yml",
        action="append",
        help="Local ingestion YAML path (required for --upload-landing).",
    )
    parser.add_argument(
        "--input-file",
        action="append",
        help="Local input file to upload into landing (repeatable, matches --ingestion-yml order).",
    )
    parser.add_argument(
        "--upload-landing",
        action="store_true",
        help="Upload input files to landing before submitting serverless jobs.",
    )
    args = parser.parse_args()

    load_dotenv(Path.cwd() / ".env")

    catalog = os.environ.get("DATABRICKS_DEFAULT_CATALOG")
    schema = os.environ.get("DATABRICKS_DEFAULT_SCHEMA")
    if not catalog or not schema:
        raise ValueError("DATABRICKS_DEFAULT_CATALOG and DATABRICKS_DEFAULT_SCHEMA must be set in .env")

    # In two-schema layouts (raw/standard separate from curated/dbt-target),
    # COI_DBX_STANDARD_* overrides target the standard schema specifically.
    standard_catalog = os.environ.get("COI_DBX_STANDARD_CATALOG") or catalog
    standard_schema = os.environ.get("COI_DBX_STANDARD_SCHEMA") or schema
    landing_base = os.environ.get("COI_DBX_LANDING_BASE")

    volume_base = f"/Volumes/{catalog}/{schema}/{args.volume}"
    script_path = f"dbfs:{volume_base}/databricks_local_ingest.py"

    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE")
    client = WorkspaceClient(profile=profile) if profile else WorkspaceClient()

    if args.upload_landing:
        if not args.input_file or not args.local_ingestion_yml:
            raise ValueError("--upload-landing requires --input-file and --local-ingestion-yml")
        if len(args.input_file) != len(args.ingestion_yml):
            raise ValueError("--input-file count must match --ingestion-yml count")
        if len(args.local_ingestion_yml) != len(args.ingestion_yml):
            raise ValueError("--local-ingestion-yml count must match --ingestion-yml count")
        for local_ingestion, input_file in zip(args.local_ingestion_yml, args.input_file):
            ingestion_path = Path(local_ingestion).resolve()
            input_path = Path(input_file).resolve()
            if not ingestion_path.exists():
                raise FileNotFoundError(f"Missing local ingestion yml: {ingestion_path}")
            if not input_path.exists():
                raise FileNotFoundError(f"Missing input file: {input_path}")
            dest = upload_to_landing(client, catalog, schema, ingestion_path, input_path)
            print(f"Uploaded to landing: {dest}")

    env_key = "coi-env"
    environments = [
        jobs.JobEnvironment(
            environment_key=env_key,
            spec=compute.Environment(
                client="4",
            ),
        )
    ]

    tasks = []
    for idx, ingestion_file in enumerate(args.ingestion_yml, start=1):
        # Strip volume prefix if user passed a full path (e.g. /Volumes/cat/schema/vol/file.yml)
        ingestion_basename = ingestion_file.rsplit("/", 1)[-1] if "/" in ingestion_file else ingestion_file
        task_key = f"raw_to_standard_{idx}"
        tasks.append(
            jobs.SubmitTask(
                task_key=task_key,
                spark_python_task=jobs.SparkPythonTask(
                    python_file=script_path,
                    parameters=[
                        "--ingestion-yml",
                        f"dbfs:{volume_base}/{ingestion_basename}",
                        "--standard-catalog",
                        standard_catalog,
                        "--standard-schema",
                        standard_schema,
                    ]
                    + (["--landing-base", landing_base] if landing_base else []),
                ),
                environment_key=env_key,
            )
        )

    # run-as identity must match the CLI-authed identity, NOT the schema's
    # created_by (that's provisioning-history metadata — often an elevated /
    # admin account that doesn't match the day-to-day CLI auth). Fall through
    # to the workspace client's current_user when neither arg nor env is set;
    # the SDK already knows who it's authed as.
    run_as_user = args.run_as_user or os.environ.get("DATABRICKS_RUN_AS_USER")
    if not run_as_user:
        try:
            run_as_user = client.current_user.me().user_name
            print(f"run-as: auto-detected CLI-authed identity {run_as_user!r}")
        except Exception as e:  # noqa: BLE001
            raise ValueError(
                "run-as user must be set via --run-as-user or DATABRICKS_RUN_AS_USER. "
                "Use the identity the Databricks CLI is authenticated as "
                "(`databricks current-user me` → user.userName), not the schema's "
                f"created_by. Auto-detect failed: {e}"
            ) from e
    run_as = jobs.JobRunAs(user_name=run_as_user)

    if args.wait:
        print(f"Submitting to workspace: {client.config.host}")
        run = client.jobs.submit_and_wait(
            run_name="coi-raw-to-standard",
            tasks=tasks,
            environments=environments,
            run_as=run_as,
        )
        print(f"Run completed: {run.run_id}")
        if run.state:
            print(f"State: {run.state.life_cycle_state} | {run.state.result_state} | {run.state.state_message}")
    else:
        print(f"Submitting to workspace: {client.config.host}")
        run = client.jobs.submit(
            run_name="coi-raw-to-standard",
            tasks=tasks,
            environments=environments,
            run_as=run_as,
        )
        print(f"Submitted run: {run.run_id}")
        try:
            _ = client.jobs.get_run(run.run_id)
        except Exception as exc:
            print(f"Warning: submitted run not found immediately. {exc}")


if __name__ == "__main__":
    main()
