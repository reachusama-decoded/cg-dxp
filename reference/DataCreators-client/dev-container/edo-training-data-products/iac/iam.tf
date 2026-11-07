data "aws_iam_policy_document" "astro_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "AWS"
      identifiers = [
        local.astro_role_arn
      ]
    }
  }
}

resource "aws_iam_role" "workload_identity_role" {
  name                 = local.workload_identity_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

data "aws_iam_policy_document" "workload_identity_policy" {
  statement {
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds",
    ]
    resources = [
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:${local.secrets_backend_prefix}/${var.deployment.name}/*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:${local.secondary_secrets_backend_prefix}/${var.deployment.name}/*",
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:/nc/cc/okta_creds/AA00002933/*" # TODO: Needs to be updated to deployment specific credential secrets in the future. This won't work for non-edo deployments
    ]
  }
  statement {
    actions = [
      "s3:ReplicateObject",
      "s3:PutObject",
      "s3:GetObject",
      "s3:RestoreObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::${local.logs_bucket_name}/*",
      "arn:aws:s3:::${local.logs_bucket_name}",
      "arn:aws:s3:::${local.xcoms_bucket_name}/*",
      "arn:aws:s3:::${local.xcoms_bucket_name}",
      "arn:aws:s3:::${local.calendar_bucket_name}/*",
      "arn:aws:s3:::${local.calendar_bucket_name}"
    ]
  }
  statement {
    actions = [
      "eks:*",
      "sts:*",
      "glue:Get*",
      "glue:BatchGet*",
      "glue:SearchTables",
      "lakeformation:Get*",
      "lakeformation:List*",
      "lakeformation:Search*",
      "lakeformation:GetDataAccess",
      "kms:Decrypt",
      "sts:AssumeRole"
    ]
    resources = ["*"]
  }
  # CG ingestion pipeline: secrets used by KPO pods (Kafka config, pipeline credentials, etc.)
  statement {
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
    ]
    resources = [
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:caspian/*",
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:AmazonMSK_*",
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:good_governance_*",
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:/nc/cc/okta_creds/*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:caspian/*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:AmazonMSK_*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:good_governance_*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:/nc/cc/okta_creds/*",
    ]
  }
}

resource "aws_iam_policy" "workload_identity_policy" {
  name        = "${var.deployment.name}-workload-identity-policy"
  description = "Policy for Astro workload identity role"
  policy      = data.aws_iam_policy_document.workload_identity_policy.json
  tags        = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "workload_identity_policy_attachment" {
  role       = aws_iam_role.workload_identity_role.name
  policy_arn = aws_iam_policy.workload_identity_policy.arn
}

resource "aws_iam_role" "secrets_backend_role" {
  name                 = local.secrets_backend_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

data "aws_iam_policy_document" "secrets_backend_policy" {
  statement {
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecrets",
      "secretsmanager:ListSecretVersionIds",
    ]
    resources = [
      "arn:aws:secretsmanager:${var.primary_region}:${local.aws_account_id}:secret:${local.secrets_backend_prefix}/${var.deployment.name}/*",
      "arn:aws:secretsmanager:${var.secondary_region}:${local.aws_account_id}:secret:${local.secondary_secrets_backend_prefix}/${var.deployment.name}/*",
    ]
  }
}

resource "aws_iam_policy" "secrets_backend_policy" {
  name        = "${var.deployment.name}-secrets-backend-policy"
  description = "Policy for Astro Secrets Backend"
  policy      = data.aws_iam_policy_document.secrets_backend_policy.json
  tags        = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "secrets_backend_policy_attachment" {
  role       = aws_iam_role.secrets_backend_role.name
  policy_arn = aws_iam_policy.secrets_backend_policy.arn
}

resource "aws_iam_role" "astronomer-aws-s3-logs-role" {
  name                 = local.aws_s3_logs_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

resource "aws_iam_policy" "astronomer-aws-s3-logs-bucket-policy" {
  name        = "${var.deployment.name}-aws-s3-logs-bucket-policy"
  description = "Astronomer aws-s3-logs bucket policy"
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
            "arn:aws:s3:::${local.logs_bucket_name}/*",
            "arn:aws:s3:::${local.logs_bucket_name}"
          ]
        }
      ]
  })
  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "astronomer-aws-s3-logs-role-attachment" {
  role       = aws_iam_role.astronomer-aws-s3-logs-role.name
  policy_arn = aws_iam_policy.astronomer-aws-s3-logs-bucket-policy.arn
}

resource "aws_s3_bucket" "aws-s3-logs-s3-bucket" {
  bucket = local.logs_bucket_name
  tags   = merge({ "backup" = "not-required-temporary-s3" }, local.merged_tags)
}

resource "aws_iam_policy" "astronomer-aws-s3-logs-eks-policy" {
  name        = "${var.deployment.name}-aws-s3-logs-policy"
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

resource "aws_iam_role_policy_attachment" "astronomer-eks-logs-role-attachment" {
  role       = aws_iam_role.astronomer-aws-s3-logs-role.name
  policy_arn = aws_iam_policy.astronomer-aws-s3-logs-eks-policy.arn
}

resource "aws_iam_role" "astronomer-aws-s3-calendar-role" {
  name                 = local.aws_s3_calendar_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

resource "aws_iam_policy" "astronomer-aws-s3-calendar-bucket-policy" {
  name        = "${var.deployment.name}-aws-s3-calendar-bucket-policy"
  description = "Astronomer aws-s3-calendar bucket policy"
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
            "arn:aws:s3:::${local.calendar_bucket_name}/*",
            "arn:aws:s3:::${local.calendar_bucket_name}"
          ]
        }
      ]
  })
  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "astronomer-aws-s3-calendar-role-attachment" {
  role       = aws_iam_role.astronomer-aws-s3-calendar-role.name
  policy_arn = aws_iam_policy.astronomer-aws-s3-calendar-bucket-policy.arn
}

resource "aws_s3_bucket" "aws-s3-calendar-s3-bucket" {
  bucket = local.calendar_bucket_name
  tags   = merge({ "backup" = "not-required-temporary-s3" }, local.merged_tags)
}

resource "aws_iam_policy" "astronomer-aws-s3-calendar-policy" {
  name        = "${var.deployment.name}-aws-s3-calendar-policy"
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


resource "aws_iam_role_policy_attachment" "astronomer-eks-calendar-role-attachment" {
  role       = aws_iam_role.astronomer-aws-s3-calendar-role.name
  policy_arn = aws_iam_policy.astronomer-aws-s3-calendar-policy.arn
}

data "aws_iam_policy_document" "emr_containers_policy" {
  statement {
    actions = [
      "emr-containers:UntagResource",
      "emr-containers:TagResource",
      "emr-containers:StartJobRun",
      "emr-containers:ListVirtualClusters",
      "emr-containers:ListTagsForResource",
      "emr-containers:ListManagedEndpoints",
      "emr-containers:ListJobRuns",
      "emr-containers:DescribeVirtualCluster",
      "emr-containers:DescribeManagedEndpoint",
      "emr-containers:DescribeJobRun",
      "emr-containers:CancelJobRun"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "emr_containers_policy" {
  name        = "${var.deployment.name}-emr-containers-policy"
  description = "Policy for EMR Containers access"
  policy      = data.aws_iam_policy_document.emr_containers_policy.json
  tags        = local.merged_tags
}

resource "aws_iam_role" "emr_containers_role" {
  name                 = local.emr_containers_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "emr_containers_policy_attachment" {
  role       = aws_iam_role.emr_containers_role.name
  policy_arn = aws_iam_policy.emr_containers_policy.arn
}

data "aws_iam_policy_document" "eks_cluster_policy" {
  statement {
    actions = [
      "eks:DescribeCluster",
      "eks:ListClusters",
      "eks:DescribeNodegroup",
      "eks:ListNodegroups"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "eks_cluster_policy" {
  name        = "${var.deployment.name}-eks-cluster-policy"
  description = "Policy for EKS Cluster access"
  policy      = data.aws_iam_policy_document.eks_cluster_policy.json
  tags        = local.merged_tags
}

resource "aws_iam_role" "eks_cluster_role" {
  name                 = local.eks_cluster_role_name
  assume_role_policy   = data.aws_iam_policy_document.astro_assume.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy_attachment" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = aws_iam_policy.eks_cluster_policy.arn
}
