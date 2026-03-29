locals {
  name_prefix = "${var.service_name}-${var.environment}"
  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecr_repository" "service" {
  name                 = local.name_prefix
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}

resource "aws_s3_bucket" "service_data" {
  bucket_prefix = "${local.name_prefix}-"
  force_destroy = var.environment != "prod"

  tags = local.tags
}

resource "aws_s3_bucket_public_access_block" "service_data" {
  bucket = aws_s3_bucket.service_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "service_data" {
  bucket = aws_s3_bucket.service_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudwatch_log_group" "service" {
  name              = "/microservices/${local.name_prefix}"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = local.tags
}
