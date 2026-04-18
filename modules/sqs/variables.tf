variable "project_name" {
  type        = string
  description = "Name of the project"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g., dev)"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
  default     = {}
}
