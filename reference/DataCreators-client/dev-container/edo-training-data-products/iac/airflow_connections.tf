########## Airflow Connections ##########
# Creates Airflow connections in AWS Secrets Manager for Astro Airflow deployments.
# Connection names are prefixed using the deployment name and environment.
# Example prefix: /<deployment_name>/<environment>/connections/<connection_name>
# Connections added by default: databricks_default and aws_default.
#
# Configuration Options:
# - `aws_secretsmanager_secret` Add for each secret you wish to create.
# - `aws_secretsmanager_secret_version` Add for each secret version you wish to create.
# - `aws_secretsmanager_secret_rotation` for automated rotation (optional).
# - `lifecycle` ignore_changes prevents overwriting existing secrets after creation (Prevents manual changes from being overridden).
#
# For new connections, make sure to uncomment the package in airflow/requirements.txt, or add if missing.
#
# For more options, refer to: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
# For connection options, see: https://registry.astronomer.io/providers
# Learn more: https://www.astronomer.io/docs/astro/secrets-backend#how-airflow-finds-connections-or-variables
#########################################

locals {
  connections_prefix = "${local.secrets_backend_prefix}/${var.deployment.name}/connections"
}

resource "aws_secretsmanager_secret" "xcom-secret" {
  name = "${local.connections_prefix}/aws_s3_xcoms"
  tags = local.merged_tags
}

resource "aws_iam_role" "astronomer-xcoms-role" {
  name = "${var.deployment.name}-xcoms-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          "AWS" : [astro_deployment.deployment.workload_identity]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}


resource "aws_secretsmanager_secret_version" "xcom-secret" {
  secret_id = aws_secretsmanager_secret.xcom-secret.id
  secret_string = jsonencode({
    description = "Connection used for xcoms in s3"
    conn_type   = "aws"
    conn_id     = "aws_s3_xcoms"
    extra = {
      role_arn = aws_iam_role.astronomer-xcoms-role.arn
    }
  })
}

resource "aws_secretsmanager_secret" "logs-secret" {
  name = "${local.connections_prefix}/aws_s3_logs"
  tags = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "logs-secret" {
  secret_id = aws_secretsmanager_secret.logs-secret.id
  secret_string = jsonencode({
    description = "Connection used for logs in s3"
    conn_type   = "aws"
    conn_id     = "aws_s3_logs"
    extra = {
      role_arn = aws_iam_role.astronomer-aws-s3-logs-role.arn
    }
  })
}

resource "aws_secretsmanager_secret" "calendar-secret" {
  name = "${local.connections_prefix}/aws_s3_calendar"
  tags = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "calendar-secret" {
  secret_id = aws_secretsmanager_secret.calendar-secret.id
  secret_string = jsonencode({
    description = "Connection used for calendar in s3"
    conn_type   = "aws"
    conn_id     = "aws_s3_calendar"
    extra = {
      role_arn = aws_iam_role.astronomer-aws-s3-calendar-role.arn
    }
  })
}

resource "aws_secretsmanager_secret" "datadog-connection" {
  name = "${local.connections_prefix}/datadog_default"
  tags = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "datadog-connection" {
  secret_id = aws_secretsmanager_secret.datadog-connection.id
  secret_string = jsonencode({
    description = "Datadog connection for astronomer platform events"
    conn_type   = "datadog"
    conn_id     = "datadog_default"
    extra = {
      api_host         = "https://api.datadoghq.com"
      api_key          = jsondecode(data.aws_secretsmanager_secret_version.datadog.secret_string)["api_key_token"]
      app_key          = jsondecode(data.aws_secretsmanager_secret_version.datadog.secret_string)["app_key_token"]
      source_type_name = "astronomer_platform"
    }
  })
}

resource "aws_secretsmanager_secret" "emr_default" {
  name        = "${local.connections_prefix}/emr_default"
  description = "EMR default connection for Airflow with IAM role"
  tags        = local.merged_tags
}

resource "aws_secretsmanager_secret_version" "emr_default" {
  secret_id = aws_secretsmanager_secret.emr_default.id
  secret_string = jsonencode({
    description = "EMR default connection for Airflow"
    conn_type   = "aws"
    conn_id     = "emr_default"
    extra = {
      role_arn = aws_iam_role.emr_containers_role.arn
    }
  })
}


resource "aws_iam_policy" "astronomer-xcoms-bucket-policy" {
  name        = "${var.deployment.name}-xcoms-bucket-policy"
  description = "Astronomer XComs bucket policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:ReplicateObject",
            "s3:PutObject",
            "s3:GetObject",
            "s3:RestoreObject",
            "s3:ListBucket",
            "s3:DeleteObject"
          ],
          "Resource" : [
            "arn:aws:s3:::${var.deployment.name}-xcoms/*",
            "arn:aws:s3:::${var.deployment.name}-xcoms"
          ]
        }
      ]
  })
  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "astronomer-xcoms-role-attachment" {
  role       = aws_iam_role.astronomer-xcoms-role.name
  policy_arn = aws_iam_policy.astronomer-xcoms-bucket-policy.arn
}

resource "aws_s3_bucket" "xcoms_s3_bucket" {
  bucket = "${var.deployment.name}-xcoms"
  tags   = merge({ "backup" = "not-required-temporary-s3" }, local.merged_tags)
}

resource "aws_iam_policy" "astronomer-eks-policy" {
  name        = "${var.deployment.name}-eks-policy"
  description = "Astronomer EKS policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "eks:*"
          ],
          "Resource" : ["*"]
        }
      ]
  })
  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "astronomer-eks-role-xcoms-attachment" {
  role       = aws_iam_role.astronomer-xcoms-role.name
  policy_arn = aws_iam_policy.astronomer-eks-policy.arn
}


resource "aws_secretsmanager_secret" "databricks_default" {
  name        = "${local.connections_prefix}/databricks_default"
  description = "Databricks default connection for Airflow"
  kms_key_id  = var.kms_key_id
  tags        = local.merged_tags
}

# EXAMPLE ROTATION LAMBDA - Uncomment and modify as needed
# resource "aws_secretsmanager_secret_rotation" "databricks_default" {
#   secret_id           = aws_secretsmanager_secret.databricks_default.id
#   rotation_lambda_arn = aws_lambda_function.example.arn
#
#   rotation_rules {
#     automatically_after_days = 89
#   }
# }

resource "aws_secretsmanager_secret_version" "databricks_default" {
  secret_id = aws_secretsmanager_secret.databricks_default.id
  secret_string = jsonencode({
    conn_type = "databricks"
    host      = "<DATABRICKS_HOST>"
    username  = "token"
    password  = "<DATABRICKS_PAT>"
  })
  lifecycle {
    ignore_changes = [secret_string] # Ignore changes to secret_string to avoid overwriting existing secrets
  }
}

resource "aws_secretsmanager_secret" "aws_default" {
  name        = "${local.connections_prefix}/aws_default"
  description = "AWS default connection for Airflow"
  kms_key_id  = var.kms_key_id
  tags        = local.merged_tags
}