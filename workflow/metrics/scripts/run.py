import numpy as np
import pandas as pd
import logging
logger = logging.getLogger('Run metric')
logger.setLevel(logging.INFO)

try:
    from sklearnex import patch_sklearn
    patch_sklearn()
except ImportError:
    logger.info('no hardware acceleration for sklearn')

from metrics import metric_map
from metrics.utils import write_metrics
from utils.io import read_anndata


input_adata = snakemake.input.h5mu
output_file = snakemake.output.metric
dataset = snakemake.wildcards.dataset
file_id = snakemake.wildcards.file_id
metric = snakemake.wildcards.metric
batch_key = snakemake.params.batch_key
label_key = snakemake.params.label_key

metrics_meta = pd.read_table(snakemake.input.metrics_meta, index_col='metric')
metric_type = metrics_meta.loc[metric]['metric_type']
metric_function = metric_map[metric]

logger.info(f'Read {input_adata} ...')
adata = read_anndata(input_adata)

if 'unintegrated' in snakemake.input.keys():
    input_unintegrated = snakemake.input.unintegrated
    logger.info(f'Read unintegrated data {input_unintegrated}...')
    unintegrated = read_anndata(input_unintegrated)
else:
    logger.info('Skip unintegrated data...')
    unintegrated = adata

output_type = adata.uns.get('output_type', 'full')
logger.info(f'Run metric {metric} for {output_type}...')
adata.obs[label_key] = adata.obs[label_key].astype(str).fillna('NA').astype('category')
score = metric_function(
    adata,
    output_type,
    batch_key=batch_key,
    label_key=label_key,
    adata_raw=unintegrated,
)

write_metrics(
    scores=[score],
    output_types=[output_type],
    metric=metric,
    metric_type=metric_type,
    batch=batch_key,
    label=label_key,
    file_id=file_id,
    dataset=dataset,
    filename=output_file
)
