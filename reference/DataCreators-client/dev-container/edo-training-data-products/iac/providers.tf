# AWS Provider needed for Airflow Connection and Variables in Secrets Manager

terraform {
  required_providers {
    astro = {
      source = "astronomer/astro"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "6.32.1"
    }
    datadog = {
      source  = "DataDog/datadog"
      version = "4.10.0"
    }
  }
}

provider "astro" {
  organization_id = var.organization_id
  token           = jsondecode(data.aws_secretsmanager_secret_version.admin.secret_string)["api_token"]
  host            = var.astronomer_host
}

provider "aws" {
  region = var.primary_region
  assume_role {
    role_arn     = var.deployment_role_arn
    session_name = "TerraformSession"
  }
}

# Datadog Provider — reads API and App keys from the astronomer/datadog secret
# (datadog secret data sources are declared in lookup.tf)
locals {
  datadog_secret = jsondecode(data.aws_secretsmanager_secret_version.datadog.secret_string)
}

provider "datadog" {
  api_key = local.datadog_secret["api_key_token"]
  app_key = local.datadog_secret["app_key_token"]
}
