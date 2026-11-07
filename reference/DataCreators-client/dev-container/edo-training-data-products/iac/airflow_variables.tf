########## Airflow Variables ##########
# Creates Airflow variables in AWS Secrets Manager for Astro Airflow deployments.
# Variable names are prefixed using the deployment name and environment.
# Example prefix: /<deployment_name>/<environment>/variables/<variable_name>
# Variables added by default: astro_platform_admin.
#
# Configuration Options:
# - `aws_secretsmanager_secret` Add for each secret you wish to create.
# - `aws_secretsmanager_secret_version` Add for each secret version you wish to create.
# - `aws_secretsmanager_secret_rotation` for automated rotation (optional).
# - `lifecycle` ignore_changes prevents overwriting existing secrets after creation (Prevents manual changes from being overridden).
#
# For more options, refer to: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
# Learn more: https://www.astronomer.io/docs/astro/secrets-backend#how-airflow-finds-connections-or-variables
#########################################

locals {
  variables_prefix = "${local.secrets_backend_prefix}/${var.deployment.name}/variables"
}

resource "aws_secretsmanager_secret" "ecr_registry_account_id" {
  name        = "${local.variables_prefix}/ecr_registry_account_id"
  description = "AWS account ID for the ECR registry"
  tags        = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "ecr_registry_account_id" {
  secret_id     = aws_secretsmanager_secret.ecr_registry_account_id.id
  secret_string = var.aws_account_id

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret" "aws_region" {
  name        = "${local.variables_prefix}/aws_region"
  description = "Primary AWS region for this deployment"
  tags        = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "aws_region" {
  secret_id     = aws_secretsmanager_secret.aws_region.id
  secret_string = var.primary_region

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret" "core_healthcheck_plaintext" {
  name = "${local.variables_prefix}/core_healthcheck_plaintext"
  tags = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "core_healthcheck_plaintext" {
  secret_id     = aws_secretsmanager_secret.core_healthcheck_plaintext.id
  secret_string = "PlainTextSampleSecret"
}

resource "aws_secretsmanager_secret" "core_healthcheck_json" {
  name = "${local.variables_prefix}/core_healthcheck_json"
  tags = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "core_healthcheck_json" {
  secret_id = aws_secretsmanager_secret.core_healthcheck_json.id
  secret_string = jsonencode({
    sample_variable_one = "one"
    sample_variable_two = 2
  })
}

resource "aws_secretsmanager_secret" "astro_platform_admin" {
  name        = "${local.variables_prefix}/astro_platform_admin"
  description = "Astro Platform Admin API Token"
  kms_key_id  = var.kms_key_id
  tags        = local.merged_tags
}

# EXAMPLE ROTATION LAMBDA - Uncomment and modify as needed
# resource "aws_secretsmanager_secret_rotation" "astro_platform_admin" {
#   secret_id           = aws_secretsmanager_secret.astro_platform_admin.id
#   rotation_lambda_arn = aws_lambda_function.example.arn
#
#   rotation_rules {
#     automatically_after_days = 89
#   }
# }

resource "aws_secretsmanager_secret_version" "astro_platform_admin" {
  secret_id = aws_secretsmanager_secret.astro_platform_admin.id
  secret_string = jsonencode({
    api_token = ""
    name      = "test-deployment-membership"
    id        = ""
  })
  lifecycle {
    ignore_changes = [secret_string] # Ignore changes to secret_string to avoid overwriting existing secrets
  }
}
