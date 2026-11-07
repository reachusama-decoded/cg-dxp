import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient, topic_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroSerializer

# from caspian.pipelines.tasks import Task  # TODO: restore once caspian.pipelines is available on cluster

logger = logging.getLogger(__name__)

@dataclass
class NotifyConfig:
    """Kafka infrastructure and connection settings."""
    topic:             str
    secret_scope:      str
    bootstrap_brokers: str
    sr_url:            str
    region:            str


@dataclass
class NotifyPayload:
    """Message payload fields published to the Kafka topic."""
    uuid:                str
    domain:              str
    dataset:             str
    model:               str
    platform:            str
    type:                str
    source:              str   = "caspian"
    current:             str   = None
    datasettype:         str   = None
    dlloadeffectivedate: str   = None

    def __post_init__(self):
        if self.datasettype == "transaction" and not self.dlloadeffectivedate:
            raise ValueError("dlloadeffectivedate is required for transaction datasets")

    def to_message(self) -> dict:
        msg = {
            "uuid":      self.uuid,
            "domain":    self.domain,
            "dataset":   self.dataset,
            "model":     self.model,
            "source":    self.source,
            "platform":  self.platform,
            "type":      self.type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # optional message values
        if self.datasettype is not None:
            msg["datasettype"] = self.datasettype
        if self.current is not None:
            msg["current"] = self.current
        if self.dlloadeffectivedate is not None:
            msg["dlloadeffectivedate"] = self.dlloadeffectivedate
        return msg


class DataNotify:
    # TODO: restore Task base class once caspian.pipelines is available on cluster
    # class DataNotify(Task):
    task_name = "data_notify"

    def __init__(self, config: NotifyConfig, payload: NotifyPayload, **kwargs):
        self.config  = config
        self.message = payload.to_message()

    @staticmethod
    def _get_dbutils():
        try:
            from databricks.sdk.runtime import dbutils
            return dbutils
        except Exception:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            return spark._jvm.com.databricks.dbutils_v1.DBUtilsHolder.dbutils()

    def execute(self):
        dbutils = self._get_dbutils()
        secret = self._get_secret(dbutils, self.config.secret_scope)
        with self._secret_root_ca(dbutils, self.config.secret_scope) as root_ca_path:
            sr          = self._get_schema_registry(self.config.sr_url, secret, root_ca_path)
            schema_str  = sr.get_latest_version(f"{self.config.topic}-value").schema.schema_str
            serializer  = AvroSerializer(
                sr, schema_str,
                lambda value, ctx: value,
                conf={"auto.register.schemas": False, "subject.name.strategy": topic_subject_name_strategy},
            )
            producer = self._create_producer(secret, root_ca_path, serializer)
            import json
            msg_str = json.dumps(self.message, indent=2, default=str)
            logger.info("PRODUCING MESSAGE [topic=%s]:\n%s", self.config.topic, msg_str)
            print(f"PRODUCING MESSAGE [topic={self.config.topic}]:\n{msg_str}", flush=True)
            producer.produce(topic=self.config.topic, key=None, value=self.message, on_delivery=self._acked)
            producer.flush()

    @staticmethod
    @contextmanager
    def _secret_root_ca(dbutils, scope: str, key: str = "rootCA"):
        cert = dbutils.secrets.get(scope, key)
        tf = NamedTemporaryFile(mode="w+t", delete=False, suffix=".pem")
        try:
            tf.write(cert)
            tf.close()
            yield tf.name
        finally:
            os.unlink(tf.name)

    @staticmethod
    def _get_secret(dbutils, scope: str, username_key: str = "username", password_key: str = "password") -> dict:
        return {
            "username": dbutils.secrets.get(scope, username_key),
            "password": dbutils.secrets.get(scope, password_key),
        }

    @staticmethod
    def _get_schema_registry(sr_url: str, secret: dict, ca_path: str) -> SchemaRegistryClient:
        return SchemaRegistryClient({
            "url":                  sr_url,
            "basic.auth.user.info": f"{secret['username']}:{secret['password']}",
            "ssl.ca.location":      ca_path,
        })

    def _create_producer(self, secret: dict, ca_path: str, value_serializer) -> SerializingProducer:
        return SerializingProducer({
            "bootstrap.servers":  self.config.bootstrap_brokers,
            "security.protocol":  "SASL_SSL",
            "sasl.mechanism":     "SCRAM-SHA-512",
            "sasl.username":      secret["username"],
            "sasl.password":      secret["password"],
            "ssl.ca.location":    ca_path,
            "value.serializer":   value_serializer,
        })

    @staticmethod
    def _acked(err, msg):
        if err is not None:
            logger.error(f"Failed to deliver message: {err}")
            raise RuntimeError(f"Kafka produce failed: {err}")
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
