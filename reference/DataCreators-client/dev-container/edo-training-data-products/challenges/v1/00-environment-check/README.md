# Challenge 00: Environment Check

This challenge verifies that the devcontainer already ships the required
toolchain. You only need to confirm authentication and service reachability.

## Goal

- Confirm the repo devcontainer has the required CLI tooling.
- Confirm you can authenticate to Databricks.
- Confirm you can run the Astro CLI.

## Toolchain

- `dpc-check`: repo-provided Databricks preflight check
- `databricks` CLI: OAuth profile configured via
   `databricks auth describe --profile DEFAULT`
- `astro` CLI: local Airflow / Astronomer tooling

## How To Use

1. From inside the devcontainer, run:

```bash
./challenges/v1/00-environment-check/verify.sh
```

2. The script prints a PASS message when the toolchain is reachable and
    Databricks auth is configured.
3. If auth is missing, run:

```bash
mise run setup:databricks
```

## Notes

- This challenge assumes the repo devcontainer workflow. The toolchain should
   already be available inside the container.
- If something is missing, prefer the documented devcontainer setup and follow
   `GETTING_STARTED.md` and `.devcontainer/README.md`.
