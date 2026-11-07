from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_compose_sets_airflow_notify_variables() -> None:
    override = _read("docker-compose.override.yml")
    assert "AIRFLOW_VAR_DATA_NOTIFY_TOPIC" in override
    assert "AIRFLOW_VAR_KAFKA_SECRET_SCOPE" in override
    assert "AIRFLOW_VAR_BOOTSTRAP_BROKERS" in override
    assert "AIRFLOW_VAR_SCHEMA_REGISTRY_URL" in override
    assert "AIRFLOW_VAR_AWS_REGION" in override


def test_atlas_dqf_cluster_is_job_cluster_compatible() -> None:
    clusters = _read("data_products/atlas_elt/variables/clusters.yml")
    assert 'spark.databricks.cluster.profile: "singleNode"' in clusters
    assert "cluster_log_conf:" not in clusters
