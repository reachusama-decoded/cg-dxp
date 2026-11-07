terraform {
  cloud {
    hostname     = "tfe.cguser.capgroup.com"
    organization = "banzai-prd"

    workspaces {
      name = "aa00003661-astronomer-iac-edo-training-prd1"
    }
  }
}
