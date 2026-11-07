# Configuration for Astronomer Deployments module.  Adjust variables as needed per environment.
environment                     = "sqa"
astronomer_host                 = "https://api.astronomer.io"
organization_id                 = "cma487t5y0bgq01lc2992s0bp"
primary_region                  = "us-east-1"
tfe_blueprint_organization_name = "banzai-qa"
astronomer_api_secret_name      = "astronomer/sqa/edo-training/deployment_admin_token"
datadog_api_secret_name         = "astronomer/datadog"
deployment_role_arn             = "arn:aws:iam:::role/AA00003661_Harness_Pipeline_Role"
permissions_boundary_arn        = "arn:aws:iam:::policy/AdminPermissionsBoundary"
kms_key_id                      = "alias/cg/internal"
aws_account_id                  = ""
autosys_url                     = "http://autorep-snp.cguser.capgroup.com:8000/cgi-bin/at1_auto_report.pl?report=cal_w_dates"

# Enable DAG-only deploys. Kept true so DAG-only deploys stay enabled across TF applies.
is_dag_deploy_enabled = true

# List of deployments to create.  This will create the name cg-<name>-<region>-<environment>.  Memory/CPU can be adjusted via the deployment_resource_map variable set in caspian-blueprint-astronomer repo
deployment = {
  name                = "edo-training-sqa1"
  description         = "Deployment edo-training-sqa1"
  type                = "DEDICATED"
  cluster_name        = "cg-shared-us-east-1-sqa"
  workspace_name      = "cg-edo-sqa"
  airflow_version     = "3.1.3"
  deployment_executor = "ASTRO"
  worker_queues = [
    {
      name               = "default"
      is_default         = true
      astro_machine      = "A5"
      min_worker_count   = 1
      max_worker_count   = 10
      worker_concurrency = 5
    }
  ]
  environment_variables = [
    {
      key       = "DAG_IGNORE_FILE_SYNTAX",
      value     = "glob",
      is_secret = false
    },
    {
      key       = "AIRFLOW__CORE__DEFAULT_TASK_EXECUTION_TIMEOUT",
      value     = "3600",
      is_secret = false
    }
  ]
  contact_emails = ["gqp@capgroup.com"]
}

# Tags applied to all resources
tags = {
  "cost-center" = "504215"
  "env-type"    = "SQA"
  "exp-date"    = "99-00-9999"
  "sd-period"   = "NA"
  "usage-id"    = "AA00003661"
}

# Datadog dashboard configuration
deploy_dashboard = true
