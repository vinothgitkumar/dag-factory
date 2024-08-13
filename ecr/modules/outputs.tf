output "arn" {
  description = "ECR repository ARN"
  value       = aws_ecr_repository.repository.arn
}

output "name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.repository.name
}

output "repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.repository.repository_url
}
