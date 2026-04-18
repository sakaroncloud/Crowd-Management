variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "user_pool_id" {
  type = string
}

variable "appsync_logs_role_arn" {
  type = string
}

variable "read_handler_arn" {
  description = "The ARN of the read_handler Lambda"
  type        = string
}

variable "lambda_role_arn" {
  description = "The ARN of the Lambda execution role"
  type        = string
}
