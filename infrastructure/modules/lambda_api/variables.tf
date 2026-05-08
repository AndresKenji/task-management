variable "project" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "db_secret_arn" {
  description = "ARN of the Secrets Manager secret holding DB connection params"
  type        = string
}

variable "user_pool_id" {
  description = "Cognito user pool ID for the JWT authorizer"
  type        = string
}

variable "user_pool_client_id" {
  description = "Cognito app client ID (audience for the JWT authorizer)"
  type        = string
}
