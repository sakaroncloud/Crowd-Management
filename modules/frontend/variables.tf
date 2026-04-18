variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The deployment environment"
  type        = string
}

variable "ui_dist_path" {
  description = "Absolute path to the built React app dist directory (run npm run build first)"
  type        = string
}
variable "web_acl_id" {
  description = "The ARN of the WAF Web ACL to attach to CloudFront"
  type        = string
  default     = ""
}
