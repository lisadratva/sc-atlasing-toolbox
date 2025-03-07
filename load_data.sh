#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../sc-atlassing-toolbox)"

snakemake \
  --profile .profiles/local \
  --configfile \
    configs/load_config.yaml \
  --snakefile $pipeline/workflow/Snakefile \
  --use-conda \
  --rerun-incomplete \
  --keep-going \
  --printshellcmds \
    $@
