variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "eu-west-2"
}


variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "crowd-monitoring"
}

variable "environment" {
  description = "The deployment environment"
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "CrowdMonitoring"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}
