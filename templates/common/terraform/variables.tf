variable "service_name" {
  description = "Logical service name (matches scaffold --name)."
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)."
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources."
  type        = string
  default     = "us-west-2"
}
