locals {
  lifecycle_policy = jsonencode({ rules = var.lifecycle_policy_rules })
  repository_name  = "${var.tenant_prefix}-${var.name}"
}

resource "aws_ecr_repository" "repository" {
  name                 = local.repository_name
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  tags = var.tags

  force_delete = var.force_delete
}

resource "aws_ecr_lifecycle_policy" "lifecycle_policy" {
  count      = length(var.lifecycle_policy_rules) == 0 ? 0 : 1
  repository = aws_ecr_repository.repository.name
  policy     = local.lifecycle_policy
}
