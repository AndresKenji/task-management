variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name, used as a prefix for resources"
  type        = string
  default     = "task-mgmt"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}
