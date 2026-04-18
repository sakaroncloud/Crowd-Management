variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "ingest_lambda_arn" {
  description = "ARN of the Ingest Lambda function"
  type        = string
}

variable "read_lambda_arn" {
  description = "ARN of the Read Lambda function"
  type        = string
}

variable "ingest_lambda_invoke_arn" {
  description = "Invoke ARN of the Ingest Lambda function"
  type        = string
}

variable "read_lambda_invoke_arn" {
  description = "Invoke ARN of the Read Lambda function"
  type        = string
}

variable "ingest_lambda_name" {
  description = "Name of the Ingest Lambda function"
  type        = string
}

variable "read_lambda_name" {
  description = "Name of the Read Lambda function"
  type        = string
}

variable "user_pool_id" {
  description = "Cognito User Pool ID"
  type        = string
}

variable "user_pool_arn" {
  description = "Cognito User Pool ARN"
  type        = string
}

variable "auth_lambda_arn" {
  description = "ARN of the Lambda Authorizer"
  type        = string
}

variable "auth_lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda Authorizer"
  type        = string
}

variable "user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  type        = string
}

variable "sqs_queue_arn" {
  description = "ARN of the SQS queue for telemetry ingestion"
  type        = string
}

variable "sqs_role_arn" {
  description = "ARN of the IAM role for API Gateway SQS integration"
  type        = string
}
