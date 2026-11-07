variable "environment" {
  description = "The environment for the deployment (e.g., dev, sqa, prd)"
  type        = string
  default     = "dev"
}

variable "astronomer_host" {
  description = "The Astronomer host URL"
  type        = string
  default     = "https://api.astronomer.io"
}

variable "organization_id" {
  description = "Organization ID for Astronomer"
  type        = string
  default     = "cma487t5y0bgq01lc2992s0bp"
}

variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary (DR) AWS region"
  type        = string
  default     = "us-west-2"
}

variable "datadog_api_secret_name" {
  description = "Name of the secret in AWS Secrets Manager that contains the Datadog API key"
  type        = string
  default     = "astronomer/datadog"
}

variable "datadog_pat_secret_name" {
  description = "Optional name of the secret in AWS Secrets Manager that contains the Datadog PAT. If null, the PAT data source is not created."
  type        = string
  default     = null
}

variable "autosys_url" {
  description = "AutoSys calendar report URL used by the autosys_scrape_calendar DAG. Varies per environment (dev/sqa/prd)."
  type        = string

  validation {
    condition     = can(regex("^https?://", var.autosys_url))
    error_message = "autosys_url must be an http(s) URL."
  }
}

variable "astronomer_api_secret_name" {
  description = "Name of the secret in AWS Secrets Manager that contains the Astronomer API key"
  type        = string
  default     = "astronomer/admin"
}

variable "deployment_role_arn" {
  description = "The ARN of the role to assume for AWS operations"
  type        = string
  default     = "arn:aws:iam::674487002452:role/AA00002933_Harness_Pipeline_Role"
}

variable "permissions_boundary_arn" {
  description = "Permissions boundary ARN for the IAM role"
  type        = string
  default     = "arn:aws:iam::674487002452:policy/AdminPermissionsBoundary"
}

variable "kms_key_id" {
  description = "KMS Key ID for encrypting secrets in AWS Secrets Manager"
  type        = string
  default     = "alias/aws-datalakefoundation-dev/useast1/secretsmanager/0/kek"
}

variable "aws_account_id" {
  description = "AWS Account ID for role ARN construction"
  type        = string
  default     = "674487002452"
}

variable "tfe_blueprint_organization_name" {
  description = "TFE organization name hosting the Astronomer blueprint modules (e.g., banzai-dev, banzai-qa, banzai-prd)"
  type        = string
}

variable "is_dag_deploy_enabled" {
  description = "Enable DAG-only deploys. Defaults to true so DAG-only deploys stay enabled across TF applies."
  type        = bool
  default     = true
}

variable "deployment" {
  description = "Deployment to create"
  type = object({
    name                = string
    description         = string
    type                = string
    cluster_name        = string
    workspace_name      = string
    airflow_version     = string
    deployment_executor = string
    worker_queues = optional(set(object({
      name               = string
      is_default         = bool
      astro_machine      = optional(string)
      node_pool_id       = optional(string)
      max_worker_count   = number
      min_worker_count   = number
      worker_concurrency = number
    })), [])
    contact_emails = optional(list(string), [])
    environment_variables = optional(list(object({
      key       = string
      value     = string
      is_secret = optional(bool, false)
    })), [])
  })

  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+", var.deployment.airflow_version))
    error_message = "deployment.airflow_version must be a dotted numeric version (e.g., \"2.9.1\" or \"3.0.0\"); required by local.is_airflow_v2."
  }
}

variable "deploy_dashboard" {
  description = "Whether to deploy the Datadog dashboard for this Astronomer deployment. Set to false to destroy the dashboard without removing the code."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to AWS resources"
  type        = map(string)
  default = {
    "cost-center" = "FILL_COST_CENTER"
    "env-type"    = "DEV"
    "exp-date"    = "99-00-9999"
    "sd-period"   = "NA"
    "usage-id"    = "FILL_ATM_ID"
  }
}