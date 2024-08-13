module "ecr" {
  source        = "git@github.com:reponame.git//modules/ecr?ref=feature-branch"
  tenant_prefix = var.tenant_prefix
  name          = var.name
}
