data "aws_secretsmanager_secret" "datadog" {
  name = var.datadog_api_secret_name
}

data "aws_secretsmanager_secret_version" "datadog" {
  secret_id = data.aws_secretsmanager_secret.datadog.id
}

data "aws_secretsmanager_secret" "datadog_pat" {
  count = var.datadog_pat_secret_name != null ? 1 : 0
  name  = var.datadog_pat_secret_name
}

data "aws_secretsmanager_secret_version" "datadog_pat" {
  count     = var.datadog_pat_secret_name != null ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.datadog_pat[0].id
}

data "aws_secretsmanager_secret" "admin" {
  name = var.astronomer_api_secret_name
}

data "aws_secretsmanager_secret_version" "admin" {
  secret_id = data.aws_secretsmanager_secret.admin.id
}

data "terraform_remote_state" "blueprint" {
  backend = "remote"
  config = {
    hostname     = "tfe.cguser.capgroup.com"
    organization = var.tfe_blueprint_organization_name
    workspaces = {
      name = "aa00002933-caspian-blueprint-astronomer-${local.tf_env}"
    }
  }
}

data "terraform_remote_state" "kafka" {
  backend = "remote"
  config = {
    hostname     = "tfe.cguser.capgroup.com"
    organization = var.tfe_blueprint_organization_name
    workspaces = {
      name = "aa00002933-caspian-blueprint-confluent-kafka-${local.tf_env}"
    }
  }
}
