# Astronomer Infrastructure as Code (IAC)

[![Terraform](https://img.shields.io/badge/Terraform-IAC-7C3AED)](https://terraform.io)
[![Astronomer](https://img.shields.io/badge/Astronomer-Platform-FF6B35)](https://astronomer.io)
[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900)](https://aws.amazon.com)

This Terraform project provisions and configures Astronomer deployments with the necessary AWS IAM roles, secrets management, and environment configurations.

This is platform provisioning reference, outside assigned learner practice. The configuration uses Terraform Enterprise state, AWS roles/secrets and Datadog integration. The platform owner supplies environment values and approves changes.

## Vended IAC Structure

``` text
config/
└── deployment/
    ├── dev1/                       # Development environment
    │   ├── backend.hcl             # Backend configuration
    │   ├── dev1_tfe_backend.config # TFE workspace
    │   └── terraform.auto.tfvars   # Environment variables
    ├── sqa1/                       # Staging environment
    │   ├── backend.hcl             # Backend configuration
    │   ├── sqa1_tfe_backend.config # TFE workspace
    │   └── terraform.auto.tfvars   # Environment variables
    └── prd1/                       # Production environment
        ├── backend.hcl             # Backend configuration
        ├── prd1_tfe_backend.config # TFE workspace
        └── terraform.auto.tfvars   # Environment variables
airflow_connections.tf  # For creating connections in secrets manager
airflow_variables.tf    # For creating variables in secrets manager
main.tf                 # Mapping of variables to module "deployments"
outputs.tf              # Sets TFE outputs for reference
variables.tf            # Lists variables that need to be provided
```

The configuration covers Astronomer deployments, AWS IAM boundaries, Secrets Manager, Datadog and environment-specific Terraform state.

## Deployment/Environment Configuration

### Core Variables

| Variable | Type | Description | Default | Required |
|----------|------|-------------|---------|----------|
| `environment` | `string` | Deployment environment | `"dev"` | No |
| `astronomer_host` | `string` | Astronomer API host URL | `"https://api.astronomer.io"` | No |
| `organization_id` | `string` | Astronomer organization ID | `"cma487t5y0bgq01lc2992s0bp"` | No |
| `primary_region` | `string` | Primary AWS region | `"us-east-1"` | No |
| `permissions_boundary_arn` | `string` | IAM permissions boundary ARN | - | **Yes** |

### Terraform Enterprise Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `tfe_blueprint_organization_name` | TFE organization name | `"banzai-dev"` |
| `tfe_blueprint_workspace_name` | TFE workspace name | `"aa00002933-caspian-blueprint-astronomer-dev1"` |

### Secrets Configuration

| Secret Name | Purpose | Content |
|-------------|---------|---------|
| `astronomer/admin` | Astronomer API authentication | `{"api_key": "your-api-key"}` |
| `astronomer/datadog` | Datadog monitoring integration | `{"api_key": "dd-api-key", "app_key": "dd-app-key"}` |

### Deployment Configuration

The `deployment` variable defines the Astronomer deployment to create:

```hcl
deployment = {
  name                = "core-default-deployment"
  description         = "Core Default Deployment for EDO"
  type                = "DEDICATED"
  cluster_name        = "cg-shared-us-east-1-dev"
  workspace_name      = "cg-edo-dev"
  airflow_version     = "2.10.5"
  deployment_executor = "KUBERNETES"
  
  # Optional: Custom worker queues
  worker_queues = [
    {
      name               = "default"
      is_default         = true
      max_worker_count   = 10
      min_worker_count   = 1
      worker_concurrency = 16
    }
  ]
  
  # Contact information
  contact_emails = ["dev-team@example.com"]
  
  # Environment variables
  environment_variables = [
    {
      key       = "DAG_IGNORE_FILE_SYNTAX"
      value     = "glob"
      is_secret = false
    },
    {
      key       = "AIRFLOW__CORE__DEFAULT_TASK_EXECUTION_TIMEOUT"
      value     = "3600"
      is_secret = false
    }
  ]
}
```

## Executing Locally

### Required Tools

- **Terraform** (>= 1.0)

  ```bash
  # macOS
  brew install terraform
  
  # Verify installation
  terraform version
  ```

- **AWS CLI** (configured with appropriate credentials)

  ```bash
  # Install AWS CLI
  brew install awscli
  
  # Configure credentials
  aws configure
  
  # Verify access
  aws sts get-caller-identity
  ```

- **Terraform Enterprise Access**

  ```bash
  # Login to TFE
  terraform login tfe.cguser.capgroup.com
  ```

### Access Requirements

| Requirement | Description | Validation |
|-------------|-------------|------------|
| **Astronomer Account** | Access to Astronomer API | `curl -H "Authorization: Bearer $TOKEN" https://api.astronomer.io/v1/organizations` |
| **AWS IAM Permissions** | Deployment role access | `aws sts assume-role --role-arn <deployment-role-arn>` |
| **TFE Workspace** | Terraform Enterprise workspace | Login to `tfe.cguser.capgroup.com` |
| **Secrets Manager** | API keys stored in AWS | `aws secretsmanager describe-secret --secret-id astronomer/admin` |

### Execution steps

Run the following only in an authorised platform workspace after reviewing the plan. Learner challenges do not apply or destroy infrastructure.

#### 1. Plan and Apply

```bash
# Navigate to IAC directory
cd iac

# Initialize Terraform with environment-specific backend
terraform init -backend-config=config/deployment/dev1/backend.hcl

# Plan changes
terraform plan -var-file=config/deployment/dev1/terraform.auto.tfvars

# Apply changes
terraform apply -var-file=config/deployment/dev1/terraform.auto.tfvars
```

#### 2. Verify Deployment

```bash
# Check outputs
terraform output

# Verify deployment in Astronomer
terraform output deployments
```

#### 3. Update Configuration

```bash
# Modify terraform.auto.tfvars
vi config/deployment/dev1/terraform.auto.tfvars

# Plan and apply changes
terraform plan -var-file=config/deployment/dev1/terraform.auto.tfvars
terraform apply -var-file=config/deployment/dev1/terraform.auto.tfvars
```

#### 4. Destroy Resources (if needed)

```bash
# Destroy deployment
terraform plan -destroy -var-file=config/deployment/dev1/terraform.auto.tfvars -out=destroy.tfplan
terraform apply "destroy.tfplan"
```

## Resources

### Internal Documentation

- **Terraform Enterprise**: `https://tfe.cguser.capgroup.com`
- **Module Registry**: `https://tfe.cguser.capgroup.com/cgregistry`
- **Caspian Platform Docs**: `https://devhub.capgroup.com/docs/default/component/caspian-platform-docs`

### External Documentation

- **Terraform**: [https://terraform.io/docs](https://terraform.io/docs)
- **Astronomer**: [https://docs.astronomer.io](https://docs.astronomer.io)
- **AWS IAM**: [https://docs.aws.amazon.com/iam](https://docs.aws.amazon.com/iam)

### Support Contacts

- **Platform Engineering Team**: [Caspian Teams Channel](https://teams.microsoft.com/l/channel/19%3Ae2680301eab549e9acdb12152fa690de%40thread.tacv2/Caspian%20C4E%20Support?groupId=17f9ec8b-6777-41fd-83f8-e505bd401595&tenantId=41b8c056-2dc3-438d-99ee-61e00287adfe)

## Template Details

- **Maintained by**: Caspian Platform Team
- **Version**: 0.0.1
- **Last Updated**: October 2025  
- **Contact**: [Teams Channel](https://teams.microsoft.com/l/channel/19%3Ae2680301eab549e9acdb12152fa690de%40thread.tacv2/Caspian%20C4E%20Support?groupId=17f9ec8b-6777-41fd-83f8-e505bd401595&tenantId=41b8c056-2dc3-438d-99ee-61e00287adfe)
