from datetime import timedelta

from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from blueprint import BaseModel, Blueprint, Field


class KafkaNotifyConfig(BaseModel):
    # --- per-task runtime values (from xcom) ---
    xcom_pull_task: str
    model:          str

    # --- Databricks compute ---
    cluster_id:  str   # existing all-purpose cluster ID
    python_file: str   # workspace path to run_data_notify.py
                       # e.g. /Workspace/<project>/<app>/.bundle/asset_reference_data/dev/files/python/run_data_notify.py

    # --- Kafka / notify infra (Airflow variable templates) ---
    kafka_topic:          str = Field(default="{{ var.value.data_notify_topic }}")
    secret_scope:         str = Field(default="{{ var.value.kafka_secret_scope }}")
    bootstrap_brokers:    str = Field(default="{{ var.value.bootstrap_brokers }}")
    schema_registry_url:  str = Field(default="{{ var.value.schema_registry_url }}")
    platform:             str = Field(default="caspian-training")
    aws_region:           str = Field(default="{{ var.value.aws_region }}")
    source:               str = Field(default="caspian")

    # --- operator config ---
    databricks_conn_id:  str = Field(default="caspian-training-databricks")
    retries:             int = 3
    retry_delay_seconds: int = 30


class KafkaNotify(Blueprint[KafkaNotifyConfig]):
    def render(self, config: KafkaNotifyConfig) -> DatabricksSubmitRunOperator:
        xcom = config.xcom_pull_task
        return DatabricksSubmitRunOperator(
            task_id=self.step_id,
            databricks_conn_id=config.databricks_conn_id,
            retries=config.retries,
            retry_exponential_backoff=True,
            retry_delay=timedelta(seconds=config.retry_delay_seconds),
            deferrable=True,
            json={
                "existing_cluster_id": config.cluster_id,
                "spark_python_task": {
                    "python_file": config.python_file,
                    "parameters": [
                        # --- infra (static per environment) ---
                        "--topic",             config.kafka_topic,
                        "--secret_scope",      config.secret_scope,
                        "--bootstrap_brokers", config.bootstrap_brokers,
                        "--sr_url",            config.schema_registry_url,
                        "--platform",          config.platform,
                        "--region",            config.aws_region,
                        "--source",            config.source,
                        # --- runtime (from upstream xcom) ---
                        "--model",  config.model,
                        "--domain",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['domain'] | default('NA', True) }}",
                        "--dataset",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['dataset'] | default('NA', True) }}",
                        "--uuid",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['uuid'] | default('NA', True) }}",
                        "--type",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['operation_type'] | default('nochange', True) }}",
                        "--current",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['current'] | default('NA', True) }}",
                        "--datasettype",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['dataset_type'] | default('NA', True) }}",
                        "--dlloadeffectivedate",
                        "{{ task_instance.xcom_pull(task_ids='" + xcom + "', key='return_value')['app_cycle_date'] | default('NA', True) }}",
                    ],
                },
            },
        )
