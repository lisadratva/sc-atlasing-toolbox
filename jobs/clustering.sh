#!/bin/bash

## bsub parameters

# BSUB -q gpu-normal
# BSUB -o /nfs/team205/ld21/repos/sc-atlassing-toolbox/jobs/job_12.out		# output file
# BSUB -e /nfs/team205/ld21/repos/sc-atlassing-toolbox/jobs/job_12.err		# error file
# BSUB -G team205
# BSUB -J preprocess
# BSUB -R "select[mem>600GB] rusage[mem=600GB]"
# BSUB -M 600GB
# BSUB -n 10
# BSUB -gpu "num=1:j_exclusive=yes"

## activate env

source activate snakemake
cd /nfs/team205/ld21/repos/sc-atlassing-toolbox
## run pipeline

bash t_cells_0612.sh integration_all clustering_all -c 10
## bash merge.sh doublets_all -c 10