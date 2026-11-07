# ─────────────────────────────────────────────────────────────────────────────
# Datadog Dashboard — Astronomer Deployment Health
#
# Sourced from Datadog_Dashboard_Astro and integrated into this repo's IaC.
# The dashboard is scoped to the single Astronomer deployment managed by this
# workspace.  deployment_id is derived automatically from the module output so
# it never needs to be hardcoded.
#
# Toggle with: deploy_dashboard = false  (in terraform.auto.tfvars)
# ─────────────────────────────────────────────────────────────────────────────

locals {
  # Deployment ID from the Astronomer module output.
  deployment_id = astro_deployment.deployment.id

  # Team-specific DAG and task IDs for template variable defaults.
  # Set these to the DAG/task IDs most relevant to this team.
  dag_ids  = ["*"]
  task_ids = ["*"]

  # Metric name locals
  # These map to the Astro Metrics Exporter (Prometheus/OTel) pipeline.
  # Counter metrics end with _total; gauges and timers do not.
  # To swap a metric (e.g. if the native integration becomes active), change it here.

  # Counters (_total suffix)
  metric_scheduler_heartbeat = "airflow_scheduler_heartbeat_total"
  metric_triggerer_heartbeat = "airflow_triggerer_heartbeat_total"
  metric_ti_successes        = "airflow_ti_successes_total"

  # Gauges / Timers (no _total suffix)
  metric_dags_average           = "airflow_dagrun_duration"
  metric_executor_queued_tasks  = "airflow_executor_queued_tasks"
  metric_executor_open_slots    = "airflow_executor_open_slots"
  metric_executor_running_tasks = "airflow_executor_running_tasks"
}

resource "datadog_dashboard" "astro_datadog_dashboard" {
  count       = var.deploy_dashboard ? 1 : 0
  title       = "${var.deployment.name} - Astro Dashboard"
  description = <<-EOT
    Deployment health dashboard for an Astronomer (Astro) Apache Airflow environment.
    Organized top-to-bottom for easy triage:
      1. Is my deployment healthy? (status indicators)
      2. Are my DAGs running successfully? (DAG health)
      3. Which tasks are problematic? (task drill-down + logs)
      4. Is my infrastructure healthy? (K8s / executor resources)
    Use the template variable dropdowns at the top to scope by deployment, DAG, or task.
  EOT
  layout_type      = "ordered"
  restricted_roles = []


  # ─────────────────────────────────────────────────────────────────────────────
  # SECTION 1 — IS MY DEPLOYMENT HEALTHY?
  # Big colored status indicators. Read this row first.
  # Green = good, Yellow = warning, Red = action required.
  # ─────────────────────────────────────────────────────────────────────────────
  widget {
    group_definition {
      background_color = "vivid_green"
      layout_type      = "ordered"
      show_title       = true
      title            = "Section 1 — Is My Deployment Healthy?"

      # --- Scheduler Heartbeat ---
      widget {
        query_value_definition {
          title       = "Scheduler Heartbeat"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_scheduler_heartbeat}{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 0
          y      = 0
        }
      }

      # --- Triggerer Heartbeat ---
      widget {
        query_value_definition {
          title       = "Triggerer Heartbeat"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_triggerer_heartbeat}{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 2
          y      = 0
        }
      }

      # --- DAG Parse Errors ---
      widget {
        query_value_definition {
          title       = "DAG Parse Errors"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_dag_processing_import_errors{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 2
              palette    = "white_on_yellow"
            }
            conditional_formats {
              comparator = ">"
              value      = 2
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 4
          y      = 0
        }
      }

      # --- Zombie Tasks Killed (last window) ---
      widget {
        query_value_definition {
          title       = "Zombie Tasks Killed"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow_zombies_killed_total{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_yellow"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 6
          y      = 0
        }
      }

      # --- SLA Misses ---
      widget {
        query_value_definition {
          title       = "SLA Misses"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow.sla_missed{astro_deployment_name:${var.deployment.name}}.as_count()"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 8
          y      = 0
        }
      }

      # --- Executor Open Slots ---
      widget {
        query_value_definition {
          title       = "Executor Open Slots"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_executor_open_slots}{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = ">"
              value      = 2
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 2
              palette    = "white_on_yellow"
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 2
          x      = 10
          y      = 0
        }
      }
    }
  }


  # ─────────────────────────────────────────────────────────────────────────────
  # SECTION 2 — ARE MY DAGS RUNNING SUCCESSFULLY?
  # High-level counts, which DAGs are broken, success/failure trend, schedule delays.
  # ─────────────────────────────────────────────────────────────────────────────
  widget {
    group_definition {
      background_color = "vivid_blue"
      layout_type      = "ordered"
      show_title       = true
      title            = "Section 2 — Are My DAGs Running Successfully?"

      # --- Successful Task Runs ---
      widget {
        query_value_definition {
          title       = "Successful Task Runs"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:${local.metric_ti_successes}{deploymentid:${local.deployment_id}}.as_count()"
              }
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_green"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 0
          y      = 0
        }
      }

      # --- Failed Task Runs ---
      widget {
        query_value_definition {
          title       = "Failed Task Runs"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow_ti_failures_total{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 3
          y      = 0
        }
      }

      # --- Avg Successful DAG Run Duration ---
      widget {
        query_value_definition {
          title       = "Avg Successful Run Duration"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_dags_average}{deploymentid:${local.deployment_id}}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 6
          y      = 0
        }
      }

      # --- Avg Failed DAG Run Duration ---
      widget {
        query_value_definition {
          title       = "Avg Failed Run Duration"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_dagrun_failed{deploymentid:${local.deployment_id}}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 9
          y      = 0
        }
      }

      # --- Failed Task Runs by DAG (Top List) ---
      widget {
        toplist_definition {
          title       = "Failed Task Runs by DAG  (which DAGs are broken?)"
          title_align = "left"
          title_size  = "16"

          request {
            formula {
              formula_expression = "query1"
              alias              = "Failures"
              limit {
                count = 10
                order = "desc"
              }
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow_ti_failures_total{deploymentid:${local.deployment_id}} by {dag_id}"
              }
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 2
        }
      }

      # --- Success vs Failure Timeseries ---
      widget {
        timeseries_definition {
          title       = "Task Run Success vs Failure Over Time"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "1d"

          request {
            display_type = "bars"
            formula {
              alias              = "Successes"
              formula_expression = "success"
            }
            formula {
              alias              = "Failures"
              formula_expression = "fail"
            }
            query {
              metric_query {
                name        = "success"
                aggregator  = "sum"
                data_source = "metrics"
                query       = "sum:${local.metric_ti_successes}{deploymentid:${local.deployment_id}}.as_count()"
              }
            }
            query {
              metric_query {
                name        = "fail"
                aggregator  = "sum"
                data_source = "metrics"
                query       = "sum:airflow_ti_failures_total{deploymentid:${local.deployment_id}}"
              }
            }
            style {
              palette    = "semantic"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 2
        }
      }

      # --- DAG Schedule Delay Timeseries ---
      widget {
        timeseries_definition {
          title       = "DAG Run Schedule Delay  (how late are DAGs starting?)"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "1d"

          request {
            display_type = "line"
            formula {
              alias              = "Schedule Delay"
              formula_expression = "query1"
            }
            query {
              metric_query {
                name        = "query1"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:airflow_dagrun_schedule_delay{deploymentid:${local.deployment_id}} by {dag_id}"
              }
            }
            style {
              palette    = "warm"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 6
        }
      }

      # --- SLA Misses by DAG (Top List) ---
      widget {
        toplist_definition {
          title       = "SLA Misses by DAG"
          title_align = "left"
          title_size  = "16"

          request {
            formula {
              formula_expression = "query1"
              alias              = "SLA Misses"
              limit {
                count = 10
                order = "desc"
              }
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow.sla_missed{astro_deployment_name:${var.deployment.name}} by {dag_id}.as_count()"
              }
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 6
        }
      }

      # --- DAGBag Size ---
      widget {
        query_value_definition {
          title       = "DAGs Loaded (DAGBag Size)"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_dagbag_size{deploymentid:${local.deployment_id}}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 0
          y      = 10
        }
      }

      # --- Total DAG Parse Time ---
      widget {
        query_value_definition {
          title       = "Total DAG Parse Time (s)"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_dag_processing_total_parse_time{deploymentid:${local.deployment_id}}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 3
          y      = 10
        }
      }
    }
  }


  # ─────────────────────────────────────────────────────────────────────────────
  # SECTION 3 — WHICH TASKS ARE PROBLEMATIC?
  # Use the $user-dag dropdown to focus on a specific DAG.
  # Use the $user-task dropdown to further narrow to one task.
  # ─────────────────────────────────────────────────────────────────────────────
  widget {
    group_definition {
      background_color = "vivid_purple"
      layout_type      = "ordered"
      show_title       = true
      title            = "Section 3 — Which Tasks Are Problematic?  (select a DAG with the $user-dag dropdown)"

      # --- Selected DAG: Avg Run Duration ---
      widget {
        query_value_definition {
          title       = "Selected DAG: Avg Successful Run Duration"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_dags_average}{deploymentid:${local.deployment_id},$user-dag}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 0
          y      = 0
        }
      }

      # --- Selected DAG: Avg Task Duration ---
      widget {
        query_value_definition {
          title       = "Selected DAG: Avg Task Duration"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_task_duration{deploymentid:${local.deployment_id},$user-dag}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 3
          y      = 0
        }
      }

      # --- Selected DAG: Recent Failure Count ---
      widget {
        query_value_definition {
          title       = "Selected DAG: Failure Count"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow_ti_failures_total{deploymentid:${local.deployment_id},$user-dag}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 6
          y      = 0
        }
      }

      # --- Selected DAG: Schedule Delay ---
      widget {
        query_value_definition {
          title       = "Selected DAG: Schedule Delay"
          title_align = "left"
          title_size  = "16"
          autoscale   = true
          precision   = 2

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "avg:airflow_dagrun_schedule_delay{deploymentid:${local.deployment_id},$user-dag}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 9
          y      = 0
        }
      }

      # --- Task Failures by task_id (Top List) ---
      widget {
        toplist_definition {
          title       = "Task Failures by Task  (which tasks are failing?)"
          title_align = "left"
          title_size  = "16"

          request {
            formula {
              formula_expression = "query1"
              alias              = "Failures"
              limit {
                count = 10
                order = "desc"
              }
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:airflow_ti_failures_total{deploymentid:${local.deployment_id},$user-dag} by {task_id}"
              }
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 2
        }
      }

      # --- Avg Task Duration by task_id (Top List) ---
      widget {
        toplist_definition {
          title       = "Avg Task Duration by Task  (which tasks are slow?)"
          title_align = "left"
          title_size  = "16"

          request {
            formula {
              formula_expression = "query1"
              alias              = "Avg Duration"
              limit {
                count = 10
                order = "desc"
              }
            }
            query {
              metric_query {
                aggregator  = "avg"
                data_source = "metrics"
                name        = "query1"
                query       = "avg:airflow_task_duration{deploymentid:${local.deployment_id},$user-dag,$user-task} by {task_id}"
              }
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 2
        }
      }

      # --- Task Duration Timeseries (Avg / Max / Min) ---
      widget {
        timeseries_definition {
          title          = "Task Duration Over Time  (use $user-task to focus on one task)"
          title_align    = "left"
          title_size     = "16"
          show_legend    = true
          live_span      = "1w"
          legend_columns = ["avg", "max", "min"]

          request {
            display_type = "line"
            formula {
              alias              = "Average"
              formula_expression = "avg_query"
            }
            formula {
              alias              = "Maximum"
              formula_expression = "max_query"
            }
            formula {
              alias              = "Minimum"
              formula_expression = "min_query"
            }
            query {
              metric_query {
                name        = "avg_query"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "airflow_task_duration{deploymentid:${local.deployment_id},$user-dag,$user-task} by {task_id}"
              }
            }
            query {
              metric_query {
                name        = "max_query"
                aggregator  = "max"
                data_source = "metrics"
                query       = "airflow_task_duration{deploymentid:${local.deployment_id},$user-dag,$user-task} by {task_id}"
              }
            }
            query {
              metric_query {
                name        = "min_query"
                aggregator  = "min"
                data_source = "metrics"
                query       = "airflow_task_duration{deploymentid:${local.deployment_id},$user-dag,$user-task} by {task_id}"
              }
            }
            style {
              palette    = "dog_classic"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 6
        }
      }

      # --- Task Run Count Timeseries ---
      widget {
        timeseries_definition {
          title          = "Task Run Count Over Time"
          title_align    = "left"
          title_size     = "16"
          show_legend    = true
          live_span      = "1w"
          legend_columns = ["sum"]

          request {
            display_type = "bars"
            formula {
              formula_expression = "sum1"
            }
            query {
              metric_query {
                name        = "sum1"
                data_source = "metrics"
                aggregator  = "sum"
                query       = "${local.metric_ti_successes}{deploymentid:${local.deployment_id},$user-dag,$user-task} by {task_id}.as_count()"
              }
            }
            style {
              palette    = "dog_classic"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 6
        }
      }

      # --- Log Stream ---
      widget {
        log_stream_definition {
          title       = "Logs for Selected DAG"
          title_align = "left"
          title_size  = "16"
          indexes     = []
          query       = "source:astronomer $user-dag astro_deployment_name:${var.deployment.name}"
          columns     = ["core_host", "core_service", "tag_source", "dag_id", "task_id", "queued_time", "duration"]

          show_date_column    = true
          show_message_column = true
          message_display     = "expanded-md"

          sort {
            column = "time"
            order  = "desc"
          }
        }
        widget_layout {
          height = 6
          width  = 12
          x      = 0
          y      = 10
        }
      }
    }
  }


  # ─────────────────────────────────────────────────────────────────────────────
  # SECTION 4 — IS MY INFRASTRUCTURE HEALTHY?
  # Executor load, pool slots, Kubernetes CPU/memory, resource quotas, pod terminations.
  # ─────────────────────────────────────────────────────────────────────────────
  widget {
    group_definition {
      background_color = "vivid_orange"
      layout_type      = "ordered"
      show_title       = true
      title            = "Section 4 — Is My Infrastructure Healthy?"

      # --- Executor: Queued Tasks ---
      widget {
        query_value_definition {
          title       = "Executor Queued Tasks"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_executor_queued_tasks}{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 5
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 20
              palette    = "white_on_yellow"
            }
            conditional_formats {
              comparator = ">"
              value      = 20
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 0
          y      = 0
        }
      }

      # --- Executor: Running Tasks ---
      widget {
        query_value_definition {
          title       = "Executor Running Tasks"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_executor_running_tasks}{deploymentid:${local.deployment_id}}"
              }
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 3
          y      = 0
        }
      }

      # --- Executor: Open Slots ---
      widget {
        query_value_definition {
          title       = "Executor Open Slots"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "${local.metric_executor_open_slots}{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = ">"
              value      = 2
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = "<="
              value      = 2
              palette    = "white_on_yellow"
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 6
          y      = 0
        }
      }

      # --- Pool: Starving Tasks ---
      widget {
        query_value_definition {
          title       = "Pool Starving Tasks"
          title_align = "center"
          title_size  = "16"
          autoscale   = true
          precision   = 0

          request {
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                aggregator  = "last"
                data_source = "metrics"
                name        = "query1"
                query       = "airflow_pool_starving_tasks{deploymentid:${local.deployment_id}}"
              }
            }
            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_red"
            }
          }
        }
        widget_layout {
          height = 2
          width  = 3
          x      = 9
          y      = 0
        }
      }

      # --- Executor Load: Queued vs Running Timeseries ---
      widget {
        timeseries_definition {
          title       = "Executor Load: Queued vs Running Tasks Over Time"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "4h"

          request {
            display_type = "line"
            formula {
              alias              = "Queued"
              formula_expression = "queued"
            }
            formula {
              alias              = "Running"
              formula_expression = "running"
            }
            query {
              metric_query {
                name        = "queued"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "${local.metric_executor_queued_tasks}{deploymentid:${local.deployment_id}}"
              }
            }
            query {
              metric_query {
                name        = "running"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "${local.metric_executor_running_tasks}{deploymentid:${local.deployment_id}}"
              }
            }
            style {
              palette    = "dog_classic"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 2
        }
      }

      # --- Pool Slots: Open vs Used vs Queued ---
      widget {
        timeseries_definition {
          title       = "Pool Slots: Open vs Used vs Queued"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "4h"

          request {
            display_type = "line"
            formula {
              alias              = "Open"
              formula_expression = "open_slots"
            }
            formula {
              alias              = "Used"
              formula_expression = "used_slots"
            }
            formula {
              alias              = "Queued"
              formula_expression = "queued_slots"
            }
            query {
              metric_query {
                name        = "open_slots"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:airflow_pool_open_slots{deploymentid:${local.deployment_id}}"
              }
            }
            query {
              metric_query {
                name        = "used_slots"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:airflow_pool_used_slots{deploymentid:${local.deployment_id}}"
              }
            }
            query {
              metric_query {
                name        = "queued_slots"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:airflow_pool_queued_slots{deploymentid:${local.deployment_id}}"
              }
            }
            style {
              palette    = "cool"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 2
        }
      }

      # --- Container CPU Usage by Component ---
      widget {
        timeseries_definition {
          title       = "Container CPU Usage by Component  (scheduler / worker / triggerer)"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "4h"

          request {
            display_type = "line"
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                name        = "query1"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:container_cpu_usage_seconds_total{deploymentid:${local.deployment_id}} by {container_name}"
              }
            }
            style {
              palette    = "warm"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 6
        }
      }

      # --- Container Memory Usage by Component ---
      widget {
        timeseries_definition {
          title       = "Container Memory Usage by Component"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "4h"

          request {
            display_type = "line"
            formula {
              formula_expression = "query1"
            }
            query {
              metric_query {
                name        = "query1"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:container_memory_working_set_bytes{deploymentid:${local.deployment_id}} by {container_name}"
              }
            }
            style {
              palette    = "purple"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 6
        }
      }

      # --- Kubernetes Resource Quota: Usage vs Limits ---
      widget {
        timeseries_definition {
          title       = "Namespace Resource Quota: Usage vs Hard Limits"
          title_align = "left"
          title_size  = "16"
          show_legend = true
          live_span   = "4h"

          request {
            display_type = "line"
            formula {
              alias              = "Used"
              formula_expression = "used"
            }
            formula {
              alias              = "Hard Limit"
              formula_expression = "hard"
            }
            query {
              metric_query {
                name        = "used"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:kube_resourcequota{deploymentid:${local.deployment_id},type:used} by {resource}"
              }
            }
            query {
              metric_query {
                name        = "hard"
                aggregator  = "avg"
                data_source = "metrics"
                query       = "avg:kube_resourcequota{deploymentid:${local.deployment_id},type:hard} by {resource}"
              }
            }
            style {
              palette    = "dog_classic"
              line_type  = "solid"
              line_width = "normal"
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 0
          y      = 10
        }
      }

      # --- Container Terminations by Reason (Top List) ---
      widget {
        toplist_definition {
          title       = "Container Terminations by Reason  (OOMKilled, Error, etc.)"
          title_align = "left"
          title_size  = "16"

          request {
            formula {
              formula_expression = "query1"
              alias              = "Terminations"
              limit {
                count = 10
                order = "desc"
              }
            }
            query {
              metric_query {
                aggregator  = "sum"
                data_source = "metrics"
                name        = "query1"
                query       = "sum:kube_pod_container_status_terminated_reason{deploymentid:${local.deployment_id}} by {reason}"
              }
            }
          }
        }
        widget_layout {
          height = 4
          width  = 6
          x      = 6
          y      = 10
        }
      }
    }
  }


  # ─────────────────────────────────────────────────────────────────────────────
  # TEMPLATE VARIABLES
  # astro_deployment_name and deploymentid are scoped per workspace — see variables.tf.
  # Only DAG and task selection remain as interactive dropdowns.
  # ─────────────────────────────────────────────────────────────────────────────

  # Drill into a specific DAG (used in Sections 2 and 3)
  template_variable {
    defaults = [local.dag_ids[0]]
    name     = "user-dag"
    prefix   = "dag_id"
  }

  # Drill into a specific task within the selected DAG (used in Section 3)
  template_variable {
    defaults = [local.task_ids[0]]
    name     = "user-task"
    prefix   = "task_id"
  }
}
