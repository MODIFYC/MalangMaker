variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "프로젝트 이름"
  type        = string
  default     = "malang"
}

variable "dev_user_name" {
  description = "개발용 IAM 유저 이름"
  type        = string
  default     = "malang-dev"
}