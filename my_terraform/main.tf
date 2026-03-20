terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "aws-sam-cli-managed-default-samclisourcebucket-q9vup2aib9cv"
    key    = "iam/terraform.tfstate"
    region = "ap-northeast-2"
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

# ===== 배포 전용 유저 =====
resource "aws_iam_user" "malang_deployer" {
  name = "malang-deployer"
  tags = {
    Project = var.project_name
  }
}

# ===== 배포 전용 그룹 =====
resource "aws_iam_group" "malang_deployer" {
  name = "malang-deployer"
}

# ===== 그룹 멤버십 =====
resource "aws_iam_user_group_membership" "malang_deployer" {
  user = aws_iam_user.malang_deployer.name
  groups = [
    aws_iam_group.malang_deployer.name,
  ]
}

# ===== 배포 전용 그룹 정책 =====
locals {
  deployer_policies = [
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess",
  ]
}

resource "aws_iam_group_policy_attachment" "deployer" {
  count      = length(local.deployer_policies)
  group      = aws_iam_group.malang_deployer.name
  policy_arn = local.deployer_policies[count.index]
}

# <===== lambda cold start 해결 : warmup =====>

# EventBridge 규칙 (5분마다 실행)
resource "aws_cloudwatch_event_rule" "warmup" {
  name                = "lambda-warmup"          # 원하는 이름으로
  schedule_expression = "rate(5 minutes)"        # 간격 조절 가능
  depends_on = [aws_iam_group_policy_attachment.deployer]  
}

# Lambda를 타겟으로 연결
resource "aws_cloudwatch_event_target" "warmup" {
  rule = aws_cloudwatch_event_rule.warmup.name
  arn  = "arn:aws:lambda:ap-northeast-2:212315285588:function:malang-maker-MalangMakerFunction-tEie9mM6iQvB"

  input = jsonencode({
    source = "warmup"  # 핸들러에서 감지할 키
  })
}

# EventBridge가 Lambda 호출할 수 있도록 권한 부여
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = "malang-maker-MalangMakerFunction-tEie9mM6iQvB"
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.warmup.arn
}