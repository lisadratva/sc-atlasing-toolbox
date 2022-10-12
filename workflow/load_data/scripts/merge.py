import gc
import scanpy as sc
from pprint import pprint

from utils import CELLxGENE_COLUMNS, get_union

organ = snakemake.wildcards.organ
files = snakemake.input
out_file = snakemake.output.h5ad


def read_adata(file):
    ad = sc.read(file)
    ad.obs_names = ad.uns['meta']['dataset_name'] + '-' + ad.obs.reset_index().index.astype(str)

    # keep only relevant columns
    donor_column = [ad.uns['meta']['donor_column']]
    sample_columns = [s.strip() for s in ad.uns['meta']['sample_column'].split('+')]
    columns = get_union(CELLxGENE_COLUMNS, donor_column, sample_columns)

    obs = ad.obs[columns].copy()
    obs['organ'] = organ
    obs['dataset'] = ad.uns['meta']['dataset_name']
    obs['dataset_id'] = ad.uns['meta']['dataset_id']
    obs['donor'] = ad.obs[donor_column]
    obs['sample'] = ad.obs[sample_columns].apply(lambda x: '-'.join(x), axis=1)
    del ad.obs
    ad.obs = obs

    # remove data
    del ad.uns
    del ad.layers
    del ad.raw
    del ad.obsm

    gc.collect()

    return ad


print(f'Read first file {files[0]}...')
adata = read_adata(files[0])
print(adata)

for file in files[1:]:
    print(f'Read {file}...')
    _adata = read_adata(file)
    print(_adata)
    print('Concatenate...')
    adata = sc.concat([adata, _adata], join='outer')
    del _adata
    gc.collect()

adata.uns['dataset'] = organ
adata.uns['organ'] = organ
pprint(adata)

print('Write...')
adata.write(out_file, compression='gzip')
