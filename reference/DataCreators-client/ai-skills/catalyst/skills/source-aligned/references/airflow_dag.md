# Airflow DAG Generation Prompt

Generate an Airflow DAG YAML file for orchestrating the data pipeline.

## Input

Read from source.yml and DDL:
- `domain`: Process domain (for curation domain)
- `process_name`: For ingestion DAG name
- `target_table`: Model name
- `dc`: DC tag (for tags)
- `dag.schedule_interval`: Cron schedule

## Output Structure

Generate a complete 8-task DAG:

```yaml
schedule_info:
  run_calendar: None
  schedule_interval: {schedule_interval}
  catchup: False
  start_date: !eval "pendulum.datetime(2021, 9, 1, tz='America/Los_Angeles')"
  end_date: !eval "pendulum.datetime(2999, 12, 31, tz='America/Los_Angeles')"

airflow_dag_args:
  tags: ["op-tag:sor:{dc}","op-tag:dev_pod:company"]
  default_args:
    depends_on_past: False

tasks:
  ingestion:
    depends_on: []
    template_ref: dag_exec_check_v2
    params:
      ingestion_dag: ingestion-{domain}-{process_name}
      hours: 21
      mins: 15
      dag_exec_check_timeout: 25200
  scd_curate:
    depends_on: [ingestion]
    template_ref: dbt_emr_container_operator_critical
    params:
      driver_memory: 8G
      executor_memory: 8G
      driver_cores: 4
      executor_cores: 4
      max_executors: 8
      shuffle_partitions: 100
      kryo_max: 512m
      driver_max_result: 1g
      task_model: +{target_table}
      model_name: {target_table}
  xcom:
    depends_on: [scd_curate]
    template_ref: dbt_xcom_generation_bitemporal
    params:
      configuration: /apps/casper-im-foundation/models/{dc}/{target_table}_f/{target_table}.yml
      xcom_pull_task: scd_curate_emr_xcom_pull
      dl_system_start_column: dl_system_start_timestamp
      db_name: cspn_fndn2
      operation_type: change
  dq_validation:
    depends_on: [xcom]
    template_ref: emr_spark_deequ_verify_v11
    params:
      application_name: casper-im-foundation
      dataset_name: cspn_{target_table}
      ruleset_name: cspn_{target_table}-in_motion
      input_path: !conf "{{{{ task_instance.xcom_pull(task_ids='xcom_generation', key='return_value')['current'] }}}}"
      metrics_storage_indicator: True
      rule_group: Daily
  scd_tag:
    depends_on: [dq_validation]
    template_ref: dbt_casper_tag
    params:
      model: current
      xcom_pull_task: xcom_generation
  refresh_delta_ds:
    depends_on: [scd_tag]
    template_ref: refresh_pds_dremio
    params:
      db_path: !conf "Casper Data Lake.{{{{ var.value.get('curated_zone')|replace('s3://','')|replace('s3a://','') }}}}.cspn_fndn2"
      table_name: "{target_table}"
      table_type: "Delta"
  scd_notify:
    depends_on: [refresh_delta_ds]
    template_ref: dbt_kafka_balance_notify
    params:
      model: current
      xcom_pull_task: xcom_generation
```

## Task Workflow

The 8 tasks must execute in this order:

```
ingestion → scd_curate → xcom → dq_validation → scd_tag → refresh_delta_ds → scd_notify
```

## Placeholder Replacements

| Placeholder | Source |
|-------------|--------|
| `{domain}` | source.yml `domain` |
| `{process_name}` | source.yml `sources[0]` name |
| `{target_table}` | source.yml `target_table` |
| `{dc}` | source.yml `dc` |
| `{schedule_interval}` | source.yml `dag.schedule_interval` |

## Requirements

1. **Completeness**: ALL 8 tasks must be present
2. **Never generate partial DAG** - if output would be truncated, regenerate
3. **Correct dependencies**: Each task depends on the previous
4. **Valid YAML**: Proper indentation and syntax

## Example Output

```yaml
schedule_info:
  run_calendar: None
  schedule_interval: 30 21 * * 1-5
  catchup: False
  start_date: !eval "pendulum.datetime(2021, 9, 1, tz='America/Los_Angeles')"
  end_date: !eval "pendulum.datetime(2999, 12, 31, tz='America/Los_Angeles')"

airflow_dag_args:
  tags: ["op-tag:sor:aix","op-tag:dev_pod:company"]
  default_args:
    depends_on_past: False

tasks:
  ingestion:
    depends_on: []
    template_ref: dag_exec_check_v2
    params:
      ingestion_dag: ingestion-aix-aix_analyst_index_f1_v1_t1
      hours: 21
      mins: 15
      dag_exec_check_timeout: 25200
  scd_curate:
    depends_on: [ingestion]
    template_ref: dbt_emr_container_operator_critical
    params:
      driver_memory: 8G
      executor_memory: 8G
      driver_cores: 4
      executor_cores: 4
      max_executors: 8
      shuffle_partitions: 100
      kryo_max: 512m
      driver_max_result: 1g
      task_model: +analyst_index_v4
      model_name: analyst_index_v4
  xcom:
    depends_on: [scd_curate]
    template_ref: dbt_xcom_generation_bitemporal
    params:
      configuration: /apps/casper-im-foundation/models/aix/analyst_index_v4_f/analyst_index_v4.yml
      xcom_pull_task: scd_curate_emr_xcom_pull
      dl_system_start_column: dl_system_start_timestamp
      db_name: cspn_fndn2
      operation_type: change
  dq_validation:
    depends_on: [xcom]
    template_ref: emr_spark_deequ_verify_v11
    params:
      application_name: casper-im-foundation
      dataset_name: cspn_analyst_index_v4
      ruleset_name: cspn_analyst_index_v4-in_motion
      input_path: !conf "{{ task_instance.xcom_pull(task_ids='xcom_generation', key='return_value')['current'] }}"
      metrics_storage_indicator: True
      rule_group: Daily
  scd_tag:
    depends_on: [dq_validation]
    template_ref: dbt_casper_tag
    params:
      model: current
      xcom_pull_task: xcom_generation
  refresh_delta_ds:
    depends_on: [scd_tag]
    template_ref: refresh_pds_dremio
    params:
      db_path: !conf "Casper Data Lake.{{ var.value.get('curated_zone')|replace('s3://','')|replace('s3a://','') }}.cspn_fndn2"
      table_name: "analyst_index_v4"
      table_type: "Delta"
  scd_notify:
    depends_on: [refresh_delta_ds]
    template_ref: dbt_kafka_balance_notify
    params:
      model: current
      xcom_pull_task: xcom_generation
```

## File Naming

Save as: `dag.yml`

## Validation

- Exactly 8 tasks present
- Correct task dependency chain
- All placeholders replaced
- Valid YAML syntax
