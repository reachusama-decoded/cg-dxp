"""Shared utilities for Kafka scripts running on Databricks."""
import logging
import os
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)


def get_dbutils():
    try:
        from databricks.sdk.runtime import dbutils
        return dbutils
    except Exception:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        return spark._jvm.com.databricks.dbutils_v1.DBUtilsHolder.dbutils()


def load_secrets(dbutils, scope, username_key="username", password_key="password", root_ca_key="rootCA"):
    username    = dbutils.secrets.get(scope, username_key)
    password    = dbutils.secrets.get(scope, password_key)
    root_ca_pem = dbutils.secrets.get(scope, root_ca_key)

    logger.info(f"SECRET CHECK — username : {'OK' if username else 'EMPTY'}")
    logger.info(f"SECRET CHECK — password : {'OK' if password else 'EMPTY'}")
    logger.info(f"SECRET CHECK — rootCA   : {'OK (' + str(len(root_ca_pem)) + ' chars)' if root_ca_pem else 'EMPTY'}")

    return username, password, root_ca_pem


def kafka_config(brokers, username, password, ca_path, extra=None):
    conf = dict(
        bootstrap_servers   = brokers.split(",") if isinstance(brokers, str) else brokers,
        security_protocol   = "SASL_SSL",
        sasl_mechanism      = "SCRAM-SHA-512",
        sasl_plain_username = username,
        sasl_plain_password = password,
        ssl_cafile          = ca_path,
    )
    if extra:
        conf.update(extra)
    return conf


def write_ca_file(root_ca_pem):
    """Write the root CA PEM to a temp file. Caller is responsible for cleanup."""
    ca_file = NamedTemporaryFile(mode="w+t", delete=False, suffix=".pem")
    ca_file.write(root_ca_pem)
    ca_file.close()
    return ca_file.name


def env(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and not value:
        raise EnvironmentError(f"Required environment variable '{key}' is not set")
    return value
