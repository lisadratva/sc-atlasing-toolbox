"""
Data filtering
"""
from pathlib import Path
from pprint import pformat
import numpy as np
import pandas as pd
import scanpy as sc
from dask import array as da
import logging
logging.basicConfig(level=logging.INFO)

from utils.io import read_anndata, write_zarr_linked
from utils.misc import dask_compute


input_file = snakemake.input[0]
output_file = snakemake.output[0]
params = dict(snakemake.params)

backed = params.get('backed', True)
dask = params.get('dask', True)
subset = params.get('subset', False)

kwargs = {
    'obs': 'obs',
    'var': 'var'
    }
adata = read_anndata(input_file, **kwargs)
logging.info(adata.__str__())
print('PARAMS', params)

mask = pd.Series(np.full(adata.n_obs, True, dtype=bool), index=adata.obs_names)
print('adata.n_obs:', adata.n_obs)
if 'remove_by_column' in params:
    logging.info('remove by columns...')
    ex_filters = params['remove_by_column']
    logging.info(pformat(ex_filters))
    for column, values in ex_filters.items():
        for vals in values:
            if Path(vals).exists():
                vals = pd.read_csv(vals, header=None)
                vals.columns = ['barcodes']
                mask = mask & ~adata.obs[column].astype(str).isin(vals.barcodes)
            else:
                logging.info(f'remove {vals} from column="{column}"...')
                vals = [str(v) for v in vals]
                mask = mask & ~adata.obs[column].astype(str).isin(vals)

logging.info('Add filtered column...')
adata.obs['filtered'] = mask
value_counts = adata.obs['filtered'].value_counts()
logging.info(value_counts)

mask_var = pd.Series(np.full(adata.n_vars, True, dtype=bool), index=adata.var_names)
if 'var_names_keep' in params:
    logging.info('remove genes except var_names_keep...')
    if Path(params['var_names_keep'][0]).exists():
        var_values = pd.read_csv(params['var_names_keep'][0], header=None)
        var_values.columns = ['genes']
        print('N genes in list:', var_values.shape) # only print number of genes
        mask_var = adata.var_names.isin(var_values.genes) # keep all genes

logging.info('Add filtered_var column...')
adata.var['filtered_var'] = mask_var
print('INFO: N Var_names before:', adata.var.shape[0], '; N Var_names after:',adata[:,adata.var.filtered_var].var.shape[0])

if subset: # and False in value_counts.index:
    kwargs |= {
        'X': 'X',
        'layers': 'layers',
        'raw': 'raw',
        'obsm': 'obsm',
        'obsp': 'obsp',
        'varm': 'varm',
        'varp': 'varp',
    }
    # filter out slots that aren't present in the input
    kwargs = {k: v for k, v in kwargs.items() if k in [f.name for f in Path(input_file).iterdir()]}
    
    logging.info('Read all slots for subsetting...')
    obs = adata.obs # save updated obs
    var = adata.var # save updated var
    adata = read_anndata(
        input_file,
        backed=backed,
        dask=dask,
        **{k: v for k, v in kwargs.items() if k not in ['obs','var']},
    )
    adata.obs = obs # updated obs
    adata.var = var # updated var
    
    logging.info('Subset data by filters...')
    adata = dask_compute(adata[adata.obs['filtered'],adata.var['filtered_var']].copy())
    logging.info(adata.__str__())

logging.info(f'Write to {output_file}...')
write_zarr_linked(
    adata,
    input_file,
    output_file,
    files_to_keep=kwargs.keys(),
)