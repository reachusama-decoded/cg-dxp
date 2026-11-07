#!/usr/bin/env bash
# Verify the reconstruction journeys on the final verifier and append them to suite.tsv.
cd /workspaces/edo-training-data-products
R=.local/live/20261005T141153Z; J=$R/journeys/reconstruction
row() { python3 $R/rerun-row.py reconstruction "$1" "$2" verify "$3" "$J/$1-$2"; }
for m in offline live; do row dbt phase-one-certified $m; row docker phase-one-certified $m; row git phase-one-certified $m; row airflow phase-one-certified $m; row dbt phase-two-proficient $m; row docker phase-two-proficient $m; done
for m in offline live; do V2_GITHUB_REPO=CONMHAB_capgroup/dc-git-training V2_GITHUB_PR=1 GH_PAGER=cat row git phase-two-proficient $m; done
echo RECON-DONE
