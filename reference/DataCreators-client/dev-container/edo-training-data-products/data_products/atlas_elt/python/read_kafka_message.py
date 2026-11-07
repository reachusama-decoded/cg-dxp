"""Reads the latest message from a Kafka topic for verification purposes."""
import argparse
import os
import sys
import uuid

try:
    _here = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _here = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, "../../.blueprints/src"))

from databricks.sdk.runtime import dbutils
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from tempfile import NamedTemporaryFile
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic",             required=True)
    parser.add_argument("--secret_scope",      required=True)
    parser.add_argument("--bootstrap_brokers", required=True)
    parser.add_argument("--sr_url",            required=True)
    parser.add_argument("--timeout",           type=float, default=30.0)
    args, _ = parser.parse_known_args()
    return args


def main():
    args = _parse_args()

    username = dbutils.secrets.get(args.secret_scope, "username")
    password = dbutils.secrets.get(args.secret_scope, "password")
    rootca   = dbutils.secrets.get(args.secret_scope, "rootCA")

    tf = NamedTemporaryFile(mode="w+t", delete=False, suffix=".pem")
    tf.write(rootca)
    tf.close()

    try:
        sr = SchemaRegistryClient({
            "url":                  args.sr_url,
            "basic.auth.user.info": f"{username}:{password}",
            "ssl.ca.location":      tf.name,
        })

        schema_str = sr.get_latest_version(f"{args.topic}-value").schema.schema_str
        deserializer = AvroDeserializer(sr, schema_str)

        # Use a unique group_id each run so we always read from the earliest offset
        group_id = f"test-consumer-{uuid.uuid4()}"
        consumer = DeserializingConsumer({
            "bootstrap.servers":    args.bootstrap_brokers,
            "security.protocol":    "SASL_SSL",
            "sasl.mechanism":       "SCRAM-SHA-512",
            "sasl.username":        username,
            "sasl.password":        password,
            "ssl.ca.location":      tf.name,
            "value.deserializer":   deserializer,
            "group.id":             group_id,
            "auto.offset.reset":    "earliest",
        })

        consumer.subscribe([args.topic])
        logger.info("Subscribed to topic %s with group %s, polling for %.1fs...", args.topic, group_id, args.timeout)

        msg = consumer.poll(timeout=args.timeout)
        if msg is None:
            logger.warning("No message received within %.1fs", args.timeout)
        elif msg.error():
            logger.error("Consumer error: %s", msg.error())
        else:
            msg_str = json.dumps(msg.value(), indent=2, default=str)
            logger.info(
                "MESSAGE RECEIVED [topic=%s partition=%d offset=%d]:\n%s",
                msg.topic(), msg.partition(), msg.offset(), msg_str,
            )
            print(f"MESSAGE RECEIVED [topic={msg.topic()} partition={msg.partition()} offset={msg.offset()}]:\n{msg_str}", flush=True)

        consumer.close()
    finally:
        os.unlink(tf.name)


if __name__ == "__main__":
    main()
