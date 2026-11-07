# Consolidated locals for the astro-deployments module
locals {
  # Required platform tags for horizontal-role governance.
  required_platform_tags = {
    "edo-managed" = "true"
  }

  # Caller-provided tags are preserved, with required platform tags enforced.
  merged_tags = merge(var.tags, local.required_platform_tags)

  # Environment-based settings
  is_high_availability  = var.environment == "dev" ? false : true
  is_cicd_enforced      = true
  is_dag_deploy_enabled = var.is_dag_deploy_enabled

  # Caspian environment mapping
  caspian_env         = var.environment == "dev" ? "dev1" : var.environment == "sqa" ? "sqa1" : var.environment == "prd" ? "prd" : var.environment
  airflow_caspian_env = var.environment == "dev" ? "dev" : var.environment == "sqa" ? "sqa1" : var.environment == "prd" ? "prd" : var.environment
  tf_env              = var.environment == "dev" ? "dev1" : var.environment == "sqa" ? "sqa1" : var.environment == "prd" ? "prd1" : var.environment

  # S3 bucket names follow the horizontal-role resource naming convention.
  # s3_bucket_prefix   = "edo-astronomer"
  logs_bucket_name = "${var.deployment.name}-logs"
  # logs_bucket_name     = "${local.s3_bucket_prefix}-${var.deployment.name}-logs"
  xcoms_bucket_name = "${var.deployment.name}-xcoms"
  # xcoms_bucket_name    = "${local.s3_bucket_prefix}-${var.deployment.name}-xcoms"
  calendar_bucket_name = "${var.deployment.name}-calendar"
  # calendar_bucket_name = "${local.s3_bucket_prefix}-${var.deployment.name}-calendar"


  # Secrets backend configuration
  secrets_backend_prefix           = "astronomer/${var.primary_region}/${var.environment}"
  secondary_secrets_backend_prefix = "astronomer/${var.secondary_region}/${var.environment}"

  # Region variants for primary and DR secrets
  regions = {
    "primary" = {
      prefix = local.secrets_backend_prefix
      suffix = ""
    }
    "dr" = {
      prefix = local.secondary_secrets_backend_prefix
      suffix = "-dr"
    }
  }

  # AWS Account ID (reusable) — passed as a variable so the module does not
  # require the AWS provider to be initialized on first-time TF execution.
  aws_account_id = var.aws_account_id

  # Data sources from remote state
  airflow_astro_runtime_map = tomap(data.terraform_remote_state.blueprint.outputs.astro_airflow_runtime_map)
  clusters                  = tomap(data.terraform_remote_state.blueprint.outputs.astro_clusters)
  workspaces                = tomap(data.terraform_remote_state.blueprint.outputs.astro_workspaces)
  deployment_resource_map   = tomap(data.terraform_remote_state.blueprint.outputs.astro_deployment_resource_map)

  # AWS IAM role configuration
  cluster_aws_id = lookup(local.clusters[var.deployment.cluster_name], "provider_account", null)
  astro_role_arn = "arn:aws:iam::${local.cluster_aws_id}:role/astro-${astro_deployment.deployment.namespace}"

  # IAM role names (used in multiple places)
  # Role names use the raw deployment name — no prefix.
  workload_identity_role_name = "${var.deployment.name}-workload-identity-role"
  secrets_backend_role_name   = "${var.deployment.name}-secrets-backend"
  aws_s3_logs_role_name       = "${var.deployment.name}-aws-s3-logs-role"
  aws_s3_calendar_role_name   = "${var.deployment.name}-aws-s3-calendar-role"
  eks_cluster_role_name       = "${var.deployment.name}-eks-cluster-role"
  emr_containers_role_name    = "${var.deployment.name}-emr-containers-role"

  # IAM role ARNs (commonly used full ARNs)
  workload_identity_role_arn = "arn:aws:iam::${local.aws_account_id}:role/${local.workload_identity_role_name}"
  secrets_backend_role_arn   = "arn:aws:iam::${local.aws_account_id}:role/${local.secrets_backend_role_name}"
  aws_s3_logs_role_arn       = "arn:aws:iam::${local.aws_account_id}:role/${local.aws_s3_logs_role_name}"

  # Airflow version detection
  is_airflow_v2 = split(".", var.deployment.airflow_version)[0] == "2"

  # NOTE: `AIRFLOW__CORE__XCOM_BACKEND` and `AIRFLOW__SECRETS__BACKEND` are set
  # in the Dockerfile (ENV) for both Airflow 2.x and 3.x so the astro_deployment
  # resource does not depend on the AWS provider or per-version conditionals here.

  # Kafka connection configuration from remote state
  # The cluster key under tenant_onboarding_output (e.g. cpz_prd_west2_cluster) is
  # discovered dynamically by matching the current environment, so the module is
  # resilient to the upstream Kafka stack relocating the cluster between regions.
  kafka_cluster_keys = keys(data.terraform_remote_state.kafka.outputs.tenant_onboarding_output)
  kafka_server = one([
    for k in local.kafka_cluster_keys : k if can(regex("_${var.environment}_", k))
  ])
  kafka_secret_name = var.environment == "dev" ? "/nc/cc/okta_creds/AA00002933/oz" : var.environment == "sqa" ? "/nc/cc/okta_creds/AA00002933/sqa" : var.environment == "prd" ? "/nc/cc/okta_creds/AA00002933/cpz" : "/nc/cc/okta_creds/AA00002933/cpz"

  # ca_cert_location, event_topic, dlq_topic are baked into the Docker image ENV
  # (they are static across all deployments), so they are not exposed here.
  kafka = {
    bootstrap_servers      = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.bootstrap_url
    auth_svr_url           = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.auth_svr_url
    auth_svr_scope         = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.auth_svr_scope
    oauth_client_id        = data.terraform_remote_state.kafka.outputs.okta_clientid
    oauth_secret_name      = local.kafka_secret_name
    idpool                 = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.idpool
    logical_broker_cluster = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.logical_broker_cluster
    logical_sr_cluster     = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.logical_sr_cluster
    schema_registry_url    = data.terraform_remote_state.kafka.outputs.tenant_onboarding_output[local.kafka_server].values.sr_url
  }
}