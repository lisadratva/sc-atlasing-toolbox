#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../sc-atlassing-toolbox)"

snakemake \
  --profile .profiles/local \
  --configfile \
    configs/outputs.yaml \
    configs/resources.yaml \
    configs/load_config.yaml \
    configs/defaults.yaml \
    configs/marker_genes.yaml \
    configs/merge.yaml \
  --snakefile $pipeline/workflow/Snakefile \
  --use-conda \
  --rerun-incomplete \
  --keep-going \
  --printshellcmds \
    $@
