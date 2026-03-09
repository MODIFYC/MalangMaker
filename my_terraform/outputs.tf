output "dev_group_arn" {
  description = "malang-dev 그룹 ARN"
  value       = aws_iam_group.malang_dev.arn
}

output "ops_group_arn" {
  description = "malang-ops 그룹 ARN"
  value       = aws_iam_group.malang_ops.arn
}

output "dev_user_arn" {
  description = "malang-dev 유저 ARN"
  value       = aws_iam_user.malang_dev.arn
}