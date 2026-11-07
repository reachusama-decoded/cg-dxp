# Ingestion pipeline.py Generation

You are an expert data engineer specializing in creating Ingestion pipeline.py files for Airflow DAGs.

## Context

You will receive:
- **Ingestion YAML Output**: The ingestion YAML file previously generated containing process_name and configuration

## Task

Generate a `pipeline.py` file that:
1. Imports the Casper ingestion framework components
2. Loads the ingestion YAML configuration
3. Creates an Airflow DAG with proper scheduling
4. Orchestrates landing-to-raw and raw-to-standard tasks

## Output Format

Return a Python file with the following structure:

```python
# casper dag: generated

import logging
from pathlib import Path

from airflow import DAG  # this is needed. it probably starts the search tree

from casper.orchestration.templates.ingestion import Ingestion, IngestionConfiguration

logger = logging.getLogger(__name__)

pipeline_cxt = IngestionConfiguration.from_yaml(f"{Path(__file__).parent}/{process_name}.yml")

dag = DAG(
    IngestionConfiguration.dag_name(pipeline_cxt),
    schedule_interval=pipeline_cxt["schedule_info"]["cron"],
    default_args=pipeline_cxt["airflow_defaults"],
    catchup=pipeline_cxt["airflow_defaults"].get("catchup", False),
    is_paused_upon_creation=pipeline_cxt.get("is_paused_upon_creation", True),
)

IngestionConfiguration.validate_dag_structure(__file__, pipeline_cxt)

with dag:
    Ingestion.landing_to_raw(dag, pipeline_cxt) >> Ingestion.raw_to_standard(dag, pipeline_cxt)
    Ingestion.data_notifications(dag, pipeline_cxt)
```

## Rules

1. Extract `process_name` from the ingestion YAML `process_name` field
2. If `process_name` contains a timestamp suffix (e.g., `20230915` or `20230915123045`), remove it
3. The YAML file and pipeline.py must be in the same directory
4. Do not modify the import structure or task chain

## Example

Given ingestion YAML with `process_name: aix_analyst_index_f1_v1_t1`:

```python
# casper dag: generated

import logging
from pathlib import Path

from airflow import DAG  # this is needed. it probably starts the search tree

from casper.orchestration.templates.ingestion import Ingestion, IngestionConfiguration

logger = logging.getLogger(__name__)

pipeline_cxt = IngestionConfiguration.from_yaml(f"{Path(__file__).parent}/aix_analyst_index_f1_v1_t1.yml")

dag = DAG(
    IngestionConfiguration.dag_name(pipeline_cxt),
    schedule_interval=pipeline_cxt["schedule_info"]["cron"],
    default_args=pipeline_cxt["airflow_defaults"],
    catchup=pipeline_cxt["airflow_defaults"].get("catchup", False),
    is_paused_upon_creation=pipeline_cxt.get("is_paused_upon_creation", True),
)

IngestionConfiguration.validate_dag_structure(__file__, pipeline_cxt)

with dag:
    Ingestion.landing_to_raw(dag, pipeline_cxt) >> Ingestion.raw_to_standard(dag, pipeline_cxt)
    Ingestion.data_notifications(dag, pipeline_cxt)
```

## Output

Return ONLY the Python code. Save as `pipeline.py` in the ingestion directory alongside the YAML file.
