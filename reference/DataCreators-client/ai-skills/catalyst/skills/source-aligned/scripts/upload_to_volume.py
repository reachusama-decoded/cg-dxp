#!/usr/bin/env python3
"""Upload local files to a Databricks Volume using databricks-sdk."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

import yaml
import argparse

from databricks.sdk import WorkspaceClient


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


def upload_files(volume_base: str, files: Iterable[Path]) -> List[str]:
    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE")
    client = WorkspaceClient(profile=profile) if profile else WorkspaceClient()
    uploaded = []
    for file_path in files:
        dest = f"{volume_base.rstrip('/')}/{file_path.name}"
        with file_path.open("rb") as f:
            client.files.upload(file_path=dest, contents=f, overwrite=True)
        uploaded.append(dest)
    return uploaded


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload files to a Databricks Volume")
    parser.add_argument("--volume", default="code", help="Volume name to upload into")
    parser.add_argument("--files", nargs="+", required=True, help="Local files to upload")
    args = parser.parse_args()

    load_dotenv(Path.cwd() / ".env")
    catalog = os.environ.get("DATABRICKS_DEFAULT_CATALOG")
    schema = os.environ.get("DATABRICKS_DEFAULT_SCHEMA")
    if not catalog or not schema:
        raise ValueError("DATABRICKS_DEFAULT_CATALOG and DATABRICKS_DEFAULT_SCHEMA must be set in .env")

    volume_base = f"/Volumes/{catalog}/{schema}/{args.volume}"

    files = [Path(p) for p in args.files]
    for f in files:
        if not f.exists():
            raise FileNotFoundError(f"Missing file: {f}")

    uploaded = upload_files(volume_base, files)
    print("Uploaded:")
    for path in uploaded:
        print(path)


if __name__ == "__main__":
    main()
