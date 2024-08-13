variable "region" {}

variable "account_id" {}

variable "tags" {
  type = map(any)

  default = {
    "created_by"  = "terraform"
    "application" = "web-app"
    "tenant"      = "optional"
    "repo"        = "reponame"
  }
}

variable "tenant_prefix" {
  default = "op"
}

variable "name" {
  default = "web-app"
}
