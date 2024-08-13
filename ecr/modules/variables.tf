variable "tenant_prefix" {
  type        = string
  description = "A short tenant prefix (ie `df` for `dogfood` tenant)."

  validation {
    condition     = length(var.tenant_prefix) >= 2 && length(var.tenant_prefix) <= 10
    error_message = "The tenant_prefix must be between 2 and 10 characters in length."
  }
}

variable "name" {
  type        = string
  description = "Name of the ECR repository (will be prefixed by tenant_prefix on creation)."
}

variable "image_tag_mutability" {
  type        = string
  description = "The tag mutability setting for the repository, must be one of: `MUTABLE` or `IMMUTABLE`."
  default     = "IMMUTABLE"
  validation {
    condition     = contains(["IMMUTABLE", "MUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be one of: `MUTABLE` or `IMMUTABLE`."
  }
}

variable "scan_on_push" {
  type        = bool
  description = "Scan images after being push to the repository (true) or not (false)."
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to assign to the resource."
  default     = {}
}

variable "lifecycle_policy_rules" {
  description = "Lifecycle policy rules - see: https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html#lifecycle_policy_parameters"
  type        = any # hack because tf doesn't like basically any more specific type here

  default = [
    {
      rulePriority : 1,
      description : "Keep last 100 images",
      selection : {
        tagStatus : "tagged",
        tagPrefixList : ["main"],
        countType : "imageCountMoreThan",
        countNumber : 100
      },
      action : {
        type : "expire"
      }
    },
    {
      rulePriority : 2,
      description : "Expire images older than 14 days",
      selection : {
        tagStatus : "any",
        countType : "sinceImagePushed",
        countUnit : "days",
        countNumber : 14
      },
      action : {
        type : "expire"
      }
    }
  ]
}

variable "force_delete" {
  description = "If true, will delete the repository even if it contains images. If false it will throw an error while trying to delete the ECR."
  default     = false
}
