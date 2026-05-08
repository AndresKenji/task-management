variable "project" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Optional custom domain. Leave empty to use the default CloudFront domain."
  type        = string
  default     = ""
}
