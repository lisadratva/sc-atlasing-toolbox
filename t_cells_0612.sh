#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../sc-atlassing-toolbox)"

snakemake \
  --profile .profiles/local \
  --configfile \
    configs/resources.yaml \
    configs/load_config.yaml \
    configs/marker_genes.yaml \
    configs/outputs.yaml \
    configs/t_cells_0612.yaml \
  --snakefile $pipeline/workflow/Snakefile \
  --use-conda \
  --rerun-incomplete \
  --keep-going \
  --printshellcmds \
    $@
