from airflow.models.dagbag import DagBag
from datetime import datetime, timedelta
import pendulum
import logging
import time
import argparse
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RunId:
    """
    Simplified DAG dependency checker that waits for upstream DAG/task completion.
    
    Two-step approach:
    1. Check lookback window for already completed runs (immediate return if found)
    2. Poll incrementally from current time forward for future runs (up to timeout limit)
    """
    task_name = "run_id"
    DEFAULT_SLEEP_INTERVAL_SECONDS = 60

    def __init__(
        self,
        external_dag_id: str,
        external_task_id: str,
        dag_exec_check_timeout: str,
        lookback_window_seconds: str = "43200",  # Default 12 hours
        check_manual_run: str = "N",
        wait_for_failed_dependency: str = "N",
        sleep_interval_seconds: str = None,
    ):
        """
        Initialize the dependency checker.
        
        Args:
            external_dag_id: ID of the upstream DAG to monitor
            external_task_id: Task ID to check, or 'dag_status_check' for DAG-level check
            dag_exec_check_timeout: Max time to wait (also used as look-ahead window)
            lookback_window_seconds: How far back to look for completed runs
            check_manual_run: Include manually triggered runs (Y/N)
            wait_for_failed_dependency: Wait for failed dependencies (Y/N)
            sleep_interval_seconds: Sleep time between polling attempts
        """
        try:
            self.external_dag_id: str = external_dag_id
            self.external_task_id: str = external_task_id
            self.dag_exec_check_timeout: int = int(dag_exec_check_timeout)
            self.lookback_window_seconds: int = int(lookback_window_seconds)
            self.check_manual_run: str = check_manual_run
            self.wait_for_failed_dependency: str = wait_for_failed_dependency
            self.sleep_interval_seconds: int = int(sleep_interval_seconds) if sleep_interval_seconds else self.DEFAULT_SLEEP_INTERVAL_SECONDS

            logger.info(f"Initialized with sleep_interval: {self.sleep_interval_seconds}s, timeout: {self.dag_exec_check_timeout}s, lookback: {self.lookback_window_seconds}s")
            print("RunId parameters:")
            print(f"  external_dag_id: {external_dag_id}")
            print(f"  external_task_id: {external_task_id}")
            print(f"  dag_exec_check_timeout: {self.dag_exec_check_timeout}")
            print(f"  lookback_window_seconds: {self.lookback_window_seconds}")
            print(f"  check_manual_run: {check_manual_run}")
            print(f"  wait_for_failed_dependency: {wait_for_failed_dependency}")
            print(f"  sleep_interval_seconds: {self.sleep_interval_seconds}")
            
        except ValueError as e:
            logger.error(f"Invalid parameter values during initialization: {e}")
            raise Exception(f"Initialization failed due to invalid parameters: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise Exception(f"Initialization failed: {e}")

    def get_successful_dagrun(self, external_dag, start_time, end_time):
        """
        Find a successful DAG run in the given time window.
        
        Args:
            external_dag: The DAG object to search
            start_time: Start of time window to search
            end_time: End of time window to search
            
        Returns:
            DAG run object if successful run found, None otherwise
        """
        print(f"Searching for DAG runs between {start_time} and {end_time}")
        
        try:
            # Get DAG runs based on manual run preference
            if self.check_manual_run.strip().upper() == 'Y':
                # Include all run types (scheduled, manual, etc.)
                ext_dagruns = external_dag.get_dagruns_between(
                    start_date=start_time, 
                    end_date=end_time
                )
            else:
                # Only include scheduled runs, filter out manual/backfill runs
                ext_dagruns = [
                    dagrun for dagrun in external_dag.get_dagruns_between(
                        start_date=start_time, 
                        end_date=end_time
                    ) if dagrun.run_type == 'scheduled'
                ]
            
            print(f"Found {len(ext_dagruns)} DAG runs in time window")
            
            # Check runs in reverse order (most recent first)
            for ext_dagrun in reversed(ext_dagruns):
                try:
                    print(f"Checking DAG run: {ext_dagrun.run_id}, state: {ext_dagrun.state}, type: {ext_dagrun.run_type}")
                    
                    # Skip failed runs unless explicitly waiting for failed dependencies
                    if ext_dagrun.state == "failed" and self.wait_for_failed_dependency.strip().upper() != 'Y':
                        print(f"Skipping failed DAG run: {ext_dagrun.run_id}")
                        continue
                    
                    # Check if DAG run is successful
                    if ext_dagrun.state == "success":
                        if self.external_task_id == "dag_status_check":
                            # DAG-level check: return if entire DAG is successful
                            print(f"Found successful DAG run: {ext_dagrun.run_id}")
                            return ext_dagrun
                        else:
                            # Task-level check: verify specific task is successful
                            try:
                                task_instance = ext_dagrun.get_task_instance(task_id=self.external_task_id)
                                if task_instance is None:
                                    print(f"Task {self.external_task_id} not found in DAG run {ext_dagrun.run_id}")
                                    continue
                                
                                print(f"Task {self.external_task_id} state: {task_instance.state}")
                                if task_instance.state == "success":
                                    print(f"Found successful task {self.external_task_id} in DAG run: {ext_dagrun.run_id}")
                                    return ext_dagrun
                                    
                            except Exception as e:
                                logger.warning(f"Error accessing task instance {self.external_task_id} in {ext_dagrun.run_id}: {e}")
                                continue  # Skip this DAG run and try next one
                    
                    elif ext_dagrun.state == "running":
                        # Log running DAGs for visibility but continue searching
                        print(f"Found running DAG run: {ext_dagrun.run_id} - will keep monitoring")
                        
                except Exception as e:
                    logger.warning(f"Error processing DAG run {ext_dagrun.run_id if 'ext_dagrun' in locals() else 'unknown'}: {e}")
                    continue  # Skip this DAG run and continue with next one
            
            # No successful runs found in this time window
            return None
            
        except Exception as e:
            logger.error(f"Error searching for DAG runs between {start_time} and {end_time}: {e}")
            raise Exception(f"Failed to search for DAG runs: {e}")

    def wait_for_external_dagrun_success(self):
        """
        Main execution method for BashSensor:
        Checks lookback window and current time for successful runs.
        Returns 0 if successful DAG run found, exits with 1 if not found (to trigger reschedule).
        """
        print("\n" + "="*50)
        print("Starting simplified DAG dependency check...")
        
        # Load the external DAG from Airflow's DAG bag
        try:
            print("Loading external DAG...")
            db = DagBag(read_dags_from_db=True)
            external_dag = db.get_dag(dag_id=self.external_dag_id)
            if external_dag is None:
                raise Exception(f"External DAG '{self.external_dag_id}' not found in DAG bag.")
            
            logger.info(f"Loaded upstream DAG: {external_dag}")
            
        except Exception as e:
            logger.error(f"Failed to load external DAG '{self.external_dag_id}': {e}")
            raise Exception(f"DAG loading failed: {e}")
        
        try:
            current_time = pendulum.now()
        except Exception as e:
            logger.error(f"Error getting current time: {e}")
            raise Exception(f"Time calculation failed: {e}")
        
        # Check lookback window for already completed runs
        try:
            lookback_start = current_time.subtract(seconds=self.lookback_window_seconds)
            lookback_end = current_time
            
            print(f"Checking window for successful runs:")
            print(f"  Window: {lookback_start} to {lookback_end}")
            
            successful_dagrun = self.get_successful_dagrun(external_dag, lookback_start, lookback_end)
            
            if successful_dagrun:
                # Found successful run - return immediately
                logger.info(f"Found successful upstream DAG run: {successful_dagrun}")
                print(f"SUCCESS: Found matching DAG run {successful_dagrun.run_id}")
                try:
                    if hasattr(successful_dagrun, 'data_interval_end') and successful_dagrun.data_interval_end:
                        print(successful_dagrun.data_interval_end.isoformat())
                except Exception as e:
                    logger.warning(f"Error formatting data_interval_end: {e}")
                return 0
                
        except Exception as e:
            logger.warning(f"Error in check: {e}.")
        
        print("No successful runs found in window. Exiting with code 1 to trigger sensor reschedule.")
        return 1

def main(
    external_dag_id,
    external_task_id,
    dag_exec_check_timeout,
    lookback_window_seconds="43200",
    check_manual_run="N",
    wait_for_failed_dependency="N",
    sleep_interval_seconds=None,
    **kwargs,
):
    """
    Main entry point for the dependency checker.
    
    Args:
        external_dag_id: Upstream DAG ID to monitor
        external_task_id: Task ID to check or 'dag_status_check' for DAG-level
        dag_exec_check_timeout: Max wait time and look-ahead window (seconds)
        lookback_window_seconds: Time to look back for completed runs (seconds)
        check_manual_run: Include manual runs (Y/N)
        wait_for_failed_dependency: Wait for failed deps (Y/N)
        sleep_interval_seconds: Sleep between polls (seconds)
        
    Returns:
        0 if successful, raises exception if failed
    """
    try:
        kwargs = {
            "external_dag_id": external_dag_id,
            "external_task_id": external_task_id,
            "dag_exec_check_timeout": dag_exec_check_timeout,
            "lookback_window_seconds": lookback_window_seconds,
            "check_manual_run": check_manual_run,
            "wait_for_failed_dependency": wait_for_failed_dependency,
            "sleep_interval_seconds": sleep_interval_seconds,
        }

        run_id = RunId(**kwargs)
        return run_id.wait_for_external_dagrun_success()
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    
    try:
        parser = argparse.ArgumentParser(description="Simplified DAG dependency checker")
        
        # Required arguments
        required_named = parser.add_argument_group("required named arguments")
        required_named.add_argument("--external_dag_id", type=str, 
                                   help="External DAG ID to monitor", required=True)
        required_named.add_argument("--external_task_id", type=str, 
                                   help="External task ID to monitor (use 'dag_status_check' for DAG-level check)", 
                                   required=True)
        required_named.add_argument("--dag_exec_check_timeout", type=str, 
                                   help="Total timeout in seconds (also used as look-ahead window)", 
                                   required=True)
        
        # Optional arguments with defaults
        parser.add_argument("--lookback_window_seconds", type=str, 
                           help="Time window to look back for already completed DAGs (default: 43200 = 12 hours)", 
                           required=False, default="43200")
        parser.add_argument("--check_manual_run", type=str, 
                           help="Include manually triggered runs (Y/N, default: N)", 
                           required=False, default="N")
        parser.add_argument("--wait_for_failed_dependency", type=str, 
                           help="Wait for failed dependencies (Y/N, default: N)",
                           required=False, default="N")
        parser.add_argument("--sleep_interval_seconds", type=str, 
                           help="Sleep interval between checks (default: 60)",
                           required=False, default=None)
        
        args = parser.parse_args()
        logger.info(f"Arguments: {args}")
        
    except Exception as e:
        logger.error(f"Error parsing command line arguments: {e}")
        sys.exit(1)
    
    try:
        result = main(
            args.external_dag_id,
            args.external_task_id,
            args.dag_exec_check_timeout,
            args.lookback_window_seconds,
            args.check_manual_run,
            args.wait_for_failed_dependency,
            args.sleep_interval_seconds,
        )
        sys.exit(result)
        
    except Exception as e:
        logger.error(f"Error in simplified dag dependency checker: {e}")
        sys.exit(1)