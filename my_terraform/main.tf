terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}
# ===== IAM User =====
resource "aws_iam_user" "malang_dev" {
  name = var.dev_user_name
}

# ===== IAM Groups =====
resource "aws_iam_group" "malang_dev" {
  name = "malang-dev"
}

resource "aws_iam_group" "malang_ops" {
  name = "malang-ops"
}

# ===== 그룹 멤버십 =====
resource "aws_iam_user_group_membership" "malang_dev" {
  user = aws_iam_user.malang_dev.name
  groups = [
    aws_iam_group.malang_dev.name,
    aws_iam_group.malang_ops.name,
  ]
}

# ===== malang-dev 그룹 정책 연결 =====
locals {
  dev_policies = [
    "arn:aws:iam::aws:policy/IAMReadOnlyAccess",
    "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorFullAccess",
  ]

  ops_policies = [
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
    "arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess",
    "arn:aws:iam::aws:policy/AWSBillingReadOnlyAccess",
  ]
}

resource "aws_iam_group_policy_attachment" "dev" {
  count      = length(local.dev_policies)
  group      = aws_iam_group.malang_dev.name
  policy_arn = local.dev_policies[count.index]
}

resource "aws_iam_group_policy_attachment" "ops" {
  count      = length(local.ops_policies)
  group      = aws_iam_group.malang_ops.name
  policy_arn = local.ops_policies[count.index]
}