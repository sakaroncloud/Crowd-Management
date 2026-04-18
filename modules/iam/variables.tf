variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
}

variable "dynamodb_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}

variable "s3_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "sns_arn" {
  description = "ARN of the SNS topic"
  type        = string
}

variable "metadata_arn" {
  description = "ARN of the DynamoDB metadata table"
  type        = string
}

