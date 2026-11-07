#!/usr/bin/env python3
"""Probe Databricks serverless runtime details."""
from __future__ import annotations

import json
import os
import platform
import sys


def main() -> None:
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        def get_conf(key: str):
            try:
                return spark.conf.get(key)
            except Exception:
                return None

        info["spark_version"] = spark.version
        info["dbx_runtime_version"] = get_conf("spark.databricks.clusterUsageTags.databricksRuntimeVersion")
        info["dbx_runtime_version_string"] = get_conf("spark.databricks.clusterUsageTags.sparkVersion")
        info["dbx_serverless"] = get_conf("spark.databricks.clusterUsageTags.serverless")
        info["dbx_cluster_name"] = get_conf("spark.databricks.clusterUsageTags.clusterName")
        info["dbx_cluster_id"] = get_conf("spark.databricks.clusterUsageTags.clusterId")
        info["dbx_env"] = get_conf("spark.databricks.clusterUsageTags.environment")
    except Exception as exc:
        info["spark_error"] = f"{type(exc).__name__}: {exc}"

    print(json.dumps(info, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
