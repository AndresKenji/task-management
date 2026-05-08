variable "project" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "host" {
  description = "Postgres host (Supabase pooler host for Lambda use)"
  type        = string
}

variable "port" {
  description = "Postgres port (use 6543 for the Supabase pooler)"
  type        = number
  default     = 6543
}

variable "database" {
  description = "Postgres database name"
  type        = string
}

variable "username" {
  description = "Postgres username"
  type        = string
}

variable "password" {
  description = "Postgres password"
  type        = string
  sensitive   = true
}
