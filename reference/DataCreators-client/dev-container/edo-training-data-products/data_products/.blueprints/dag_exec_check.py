from datetime import timedelta
from airflow.sensors.bash import BashSensor
from blueprint import BaseModel, Blueprint


class DagExecCheckConfig(BaseModel):
    executor_memory: str = "2g"
    driver_memory: str = "4g"
    dag_task_id: str = "task_std_tag_files"
    dag_exec_check_timeout: int = 36000
    lookback_window_seconds: int = 43200
    check_manual_run: str = "Y"
    wait_for_failed_dependency: str = "Y"
    sleep_interval_seconds: int = 60
    upstream_dag: str


class DagExecCheck(Blueprint[DagExecCheckConfig]):
    def render(self, config: DagExecCheckConfig) -> BashSensor:
        bash_command = (
            f"python /usr/local/airflow/data_products/.blueprints/src/dag_run_id_notify_v2.py "
            f"--external_dag_id {config.upstream_dag} "
            f"--external_task_id {config.dag_task_id} "
            f"--dag_exec_check_timeout {config.dag_exec_check_timeout} "
            f"--lookback_window_seconds {config.lookback_window_seconds} "
            f"--check_manual_run {config.check_manual_run} "
            f"--wait_for_failed_dependency {config.wait_for_failed_dependency} "
            f"--sleep_interval_seconds {config.sleep_interval_seconds}"
        )
        
        return BashSensor(
            task_id=self.step_id,
            bash_command=bash_command,
            mode="reschedule",
            poke_interval=config.sleep_interval_seconds,
            timeout=config.dag_exec_check_timeout,
            retry_exponential_backoff=True,
            retry_delay=timedelta(seconds=60),
            retries=5,
        )
