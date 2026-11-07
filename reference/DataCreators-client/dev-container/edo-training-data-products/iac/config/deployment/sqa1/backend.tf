terraform {
  cloud {
    hostname     = "tfe.cguser.capgroup.com"
    organization = "banzai-sqa"

    workspaces {
      name = "aa00003661-astronomer-iac-edo-training-sqa1"
    }
  }
}
