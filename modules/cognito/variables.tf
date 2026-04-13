variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "frontend_url" {
  description = "The production CloudFront URL of the frontend (added to Cognito callback URLs)"
  type        = string
  default     = ""
}
