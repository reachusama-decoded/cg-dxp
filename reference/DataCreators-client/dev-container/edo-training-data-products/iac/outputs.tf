# Outputs for Astronomer Deployments module.  To see output check TFE workspace after apply.

output "deployments" {
  description = "Map of Astronomer deployment details"
  value = {
    id                = astro_deployment.deployment.id
    workload_identity = astro_deployment.deployment.workload_identity
    oidc_issuer_url   = astro_deployment.deployment.oidc_issuer_url
  }
}