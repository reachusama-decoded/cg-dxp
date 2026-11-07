## Module to deploy Astronomer Deployments with best practices.  To change configuration see config/deployment/<env>/terraform.auto.tfvars.

locals {
  is_development_mode = var.environment == "dev" ? true : false
}

resource "astro_deployment" "deployment" {
  original_astro_runtime_version = lookup(local.airflow_astro_runtime_map, var.deployment.airflow_version, null)
  name                           = var.deployment.name
  description                    = var.deployment.description
  type                           = var.deployment.type
  cluster_id                     = lookup(local.clusters[var.deployment.cluster_name], "id", null)
  workspace_id                   = lookup(local.workspaces[var.deployment.workspace_name], "id", null)
  executor                       = var.deployment.deployment_executor
  worker_queues                  = contains(["CELERY", "ASTRO"], var.deployment.deployment_executor) ? var.deployment.worker_queues : null
  scheduler_size                 = try(local.deployment_resource_map[var.deployment.workspace_name][var.deployment.name]["scheduler_size"], "SMALL")
  default_task_pod_cpu           = try(local.deployment_resource_map[var.deployment.workspace_name][var.deployment.name]["default_task_pod_cpu"], "0.25")
  default_task_pod_memory        = try(local.deployment_resource_map[var.deployment.workspace_name][var.deployment.name]["default_task_pod_memory"], "0.5Gi")
  resource_quota_cpu             = try(local.deployment_resource_map[var.deployment.workspace_name][var.deployment.name]["resource_quota_cpu"], "10")
  resource_quota_memory          = try(local.deployment_resource_map[var.deployment.workspace_name][var.deployment.name]["resource_quota_memory"], "20Gi")
  is_development_mode            = local.is_development_mode
  is_high_availability           = local.is_high_availability
  is_cicd_enforced               = local.is_cicd_enforced
  is_dag_deploy_enabled          = local.is_dag_deploy_enabled
  environment_variables = concat(var.deployment.environment_variables, [
    {
      key       = "AIRFLOW__COMMON_IO__XCOM_OBJECTSTORAGE_PATH",
      value     = "s3://aws_s3_xcoms@${local.xcoms_bucket_name}/xcom",
      is_secret = false
    },
    {
      key       = "AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER"
      value     = "s3://aws_s3_logs@${local.logs_bucket_name}/logs"
      is_secret = false
    },
    {
      key       = "AIRFLOW__ASTRO_SECONDARY_LOGS__S3_BASE_LOG_FOLDER"
      value     = "s3://${local.logs_bucket_name}/logs"
      is_secret = false
    },
    {
      key       = "AIRFLOW__ASTRO_SECONDARY_LOGS__REGION"
      value     = "${var.primary_region}"
      is_secret = false
    },
    {
      key       = "AIRFLOW__ASTRO_SECONDARY_LOGS__ROLE_ARN"
      value     = local.aws_s3_logs_role_arn
      is_secret = false
    },
    {
      key       = "AIRFLOW__SECRETS__BACKEND_KWARGS"
      value     = "{\"connections_prefix\": \"${local.secrets_backend_prefix}/${var.deployment.name}/connections\", \"variables_prefix\": \"${local.secrets_backend_prefix}/${var.deployment.name}/variables\", \"role_arn\": \"${local.secrets_backend_role_arn}\"}"
      is_secret = false
    },
    {
      key = "ASTRO_DATADOG_TASK_LOGS_TAGS"
      value = join(",", [
        "astro_cluster_id:${lookup(local.clusters[var.deployment.cluster_name], "id", null)}",
        "astro_cluster_name:${var.deployment.cluster_name}",
        "astro_workspace_id:${lookup(local.workspaces[var.deployment.workspace_name], "id", null)}",
        "astro_workspace_name:${var.deployment.workspace_name}",
        "astro_deployment_name:${var.deployment.name}",
        "environment:${var.environment}"
      ])
      is_secret = false
    },
    {
      key = "AIRFLOW__METRICS__STATSD_DATADOG_TAGS"
      value = join(",", [
        "astro_cluster_id:${lookup(local.clusters[var.deployment.cluster_name], "id", null)}",
        "astro_cluster_name:${var.deployment.cluster_name}",
        "astro_workspace_id:${lookup(local.workspaces[var.deployment.workspace_name], "id", null)}",
        "astro_workspace_name:${var.deployment.workspace_name}",
        "astro_deployment_name:${var.deployment.name}",
        "environment:${var.environment}"
      ])
      is_secret = false
    },
    {
      key       = "AWS_DEFAULT_REGION"
      value     = var.primary_region
      is_secret = false
    },
    {
      key       = "TARGET_ROLE_ARN"
      value     = local.workload_identity_role_arn
      is_secret = false
    },
    {
      key       = "AIRFLOW_VAR_CASPIAN_AWS_ROLE_ARN"
      value     = local.workload_identity_role_arn
      is_secret = false
    },
    {
      key       = "AIRFLOW_VAR_AUTOSYS_URL"
      value     = var.autosys_url
      is_secret = false
    },
    {
      key       = "CASPIAN_ENV_TYPE"
      value     = local.airflow_caspian_env
      is_secret = false
    },
    {
      key       = "ASTRONOMER_DEPLOYMENT_NAME",
      value     = var.deployment.name,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__BOOTSTRAP_SERVERS",
      value     = local.kafka.bootstrap_servers,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__AUTH_SVR_URL",
      value     = local.kafka.auth_svr_url,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__AUTH_SVR_SCOPE",
      value     = local.kafka.auth_svr_scope,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__OAUTH_CLIENT_ID",
      value     = local.kafka.oauth_client_id,
      is_secret = true
    },
    {
      key       = "ASTRO__KAFKA__OAUTH_SECRET_NAME",
      value     = local.kafka.oauth_secret_name,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__IDPOOL",
      value     = local.kafka.idpool,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__LOGICAL_BROKER_CLUSTER",
      value     = local.kafka.logical_broker_cluster,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__LOGICAL_SR_CLUSTER",
      value     = local.kafka.logical_sr_cluster,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__SCHEMA_REGISTRY_URL",
      value     = local.kafka.schema_registry_url,
      is_secret = false
    },
    {
      key       = "ASTRO__KAFKA__CONSUMER_GROUP_ID"
      value     = "scaphe-consumer-${var.deployment.name}"
      is_secret = false
    }
  ])
  contact_emails = var.deployment.contact_emails != [] ? var.deployment.contact_emails : null
}
