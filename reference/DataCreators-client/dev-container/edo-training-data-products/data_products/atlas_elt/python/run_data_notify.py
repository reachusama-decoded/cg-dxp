"""Entrypoint for running DataNotify from a Databricks spark_python_task.

All configuration is supplied as CLI arguments (python_params from
DatabricksSubmitRunOperator), so this script has no dependency on cluster
environment variables and can run on any existing all-purpose cluster.
"""
import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

try:
    _here = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _here = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, "../../.blueprints/src"))

from data_notify import DataNotify, NotifyConfig, NotifyPayload


def _parse_args():
    parser = argparse.ArgumentParser(description="Run DataNotify on Databricks")

    # --- Kafka infra ---
    parser.add_argument("--topic",             required=True,  help="Kafka topic name")
    parser.add_argument("--secret_scope",      required=True,  help="Databricks secret scope for MSK creds + root CA")
    parser.add_argument("--bootstrap_brokers", required=True,  help="Comma-separated MSK broker list")
    parser.add_argument("--sr_url",            required=True,  help="Schema Registry URL")
    parser.add_argument("--platform",          required=True,  help="Platform identifier e.g. caspian-ig")
    parser.add_argument("--region",            default="us-east-1")
    parser.add_argument("--source",            default="caspian")

    # --- per-run payload (from upstream xcom via python_params) ---
    parser.add_argument("--domain",              required=True)
    parser.add_argument("--dataset",             required=True)
    parser.add_argument("--uuid",                required=True)
    parser.add_argument("--model",               required=True)
    parser.add_argument("--type",                required=True)
    parser.add_argument("--current",             default=None)
    parser.add_argument("--datasettype",         default=None)
    parser.add_argument("--dlloadeffectivedate", default=None)

    # allow unknown args so Databricks cluster-level flags don't break the script
    args, _ = parser.parse_known_args()
    return args


def _none_if_na(value: str):
    """Normalise 'NA' / empty strings (Jinja defaults) to None."""
    if value in (None, "NA", ""):
        return None
    return value


def main():
    args = _parse_args()

    config = NotifyConfig(
        topic             = args.topic,
        secret_scope      = args.secret_scope,
        bootstrap_brokers = args.bootstrap_brokers,
        sr_url            = args.sr_url,
        region            = args.region,
    )

    payload = NotifyPayload(
        uuid                = args.uuid,
        domain              = args.domain,
        dataset             = args.dataset,
        model               = args.model,
        platform            = args.platform,
        type                = args.type,
        source              = args.source,
        current             = _none_if_na(args.current),
        datasettype         = _none_if_na(args.datasettype),
        dlloadeffectivedate = _none_if_na(args.dlloadeffectivedate),
    )

    DataNotify(config=config, payload=payload).execute()


if __name__ == "__main__":
    main()
