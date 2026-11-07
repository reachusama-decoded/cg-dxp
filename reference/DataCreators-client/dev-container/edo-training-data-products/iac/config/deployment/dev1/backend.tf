terraform {
  cloud {
    hostname     = "tfe.cguser.capgroup.com"
    organization = "banzai-dev"

    workspaces {
      name = "aa00003661-astronomer-iac-edo-training-dev1"
    }
  }
}
