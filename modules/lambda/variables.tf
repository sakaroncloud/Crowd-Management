variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "lambda_role_arn" {
  description = "ARN of the Lambda Execution Role"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "metadata_table_name" {
  description = "Name of the DynamoDB metadata table"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for logs"
  type        = string
}

variable "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  type        = string
}

variable "token_param_name" {
  description = "SSM parameter name for the ingestion token"
  type        = string
}

variable "appsync_url" {
  description = "URL of the AppSync GraphQL API"
  type        = string
}

variable "dynamodb_stream_arn" {
  description = "ARN of the DynamoDB table stream"
  type        = string
}
