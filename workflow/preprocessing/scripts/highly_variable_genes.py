"""
Highly variable gene selection
- lineage specific HVGs
"""
import warnings
warnings.filterwarnings("ignore", message="The frame.append method is deprecated and will be removed from pandas in a future version.")
import scanpy as sc
from utils.io import read_anndata

input_file = snakemake.input[0]
output_file = snakemake.output[0]
n_hvgs = snakemake.params['n_hvgs']
batch_key = snakemake.params['batch']
lineage_key = snakemake.params['lineage']

print('read...')
adata = read_anndata(input_file)

adata.uns["log1p"] = {"base": None}
sc.pp.filter_genes(adata, min_cells=1)

if lineage_key is None:
    adata.obs['hvg_batch'] = adata.obs[batch_key]    
else:
    print(f'include lineage from {lineage_key}')
    adata.obs['hvg_batch'] = adata.obs[batch_key].astype(str) + '_' + adata.obs[lineage_key].astype(str)

sc.pp.highly_variable_genes(adata, n_top_genes=n_hvgs, batch_key='hvg_batch')

print('write...')
adata.write(output_file)
