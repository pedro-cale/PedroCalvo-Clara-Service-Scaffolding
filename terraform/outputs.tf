output "ecr_repository_url" {
  description = "ECR registry URL for docker push/pull."
  value       = aws_ecr_repository.service.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name (matches CI ECR_REPO pattern when ENV is set)."
  value       = aws_ecr_repository.service.name
}

output "s3_bucket_id" {
  description = "S3 bucket for service data / artifacts."
  value       = aws_s3_bucket.service_data.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN."
  value       = aws_s3_bucket.service_data.arn
}

output "cloudwatch_log_group_name" {
  description = "Log group reserved for the service runtime."
  value       = aws_cloudwatch_log_group.service.name
}
