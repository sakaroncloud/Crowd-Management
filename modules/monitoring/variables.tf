variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The deployment environment"
  type        = string
}

variable "ingest_lambda_name" {
  description = "The name of the ingestion Lambda function"
  type        = string
}

variable "read_lambda_name" {
  description = "The name of the read Lambda function"
  type        = string
}

variable "api_id" {
  description = "The ID of the API Gateway"
  type        = string
}

variable "sns_topic_arn" {
  description = "The ARN of the SNS topic for alerts"
  type        = string
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
