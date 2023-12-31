import logging
logging.basicConfig(level=logging.INFO)
from pprint import pformat
import torch
import scarches as sca
from scarches.dataset.trvae.data_handling import remove_sparsity

from utils import add_metadata, get_hyperparams, remove_slots, set_model_history_dtypes
from utils_pipeline.io import read_anndata, write_zarr_linked
from utils_pipeline.accessors import select_layer, subset_hvg

input_file = snakemake.input[0]
output_file = snakemake.output[0]
output_model = snakemake.output.model
wildcards = snakemake.wildcards
batch_key = wildcards.batch
label_key = wildcards.label
params = snakemake.params

model_params, train_params = get_hyperparams(
    hyperparams=params.get('hyperparams', {}),
    train_params=[
        'n_epochs',
        'max_epochs',
        'observed_lib_size',
        'n_samples_per_label'
    ],
)
logging.info(
    f'model parameters:\n{pformat(model_params)}\n'
    f'training parameters:\n{pformat(train_params)}'
)

# check GPU
logging.info(f'GPU available: {torch.cuda.is_available()}')

logging.info(f'Read {input_file}...')
adata = read_anndata(input_file, X='X', obs='obs', var='var', layers='layers', raw='raw', uns='uns')
adata.X = select_layer(adata, params['norm_counts'], force_sparse=True).astype('float32')

# prepare data for model
adata = subset_hvg(adata)
adata = remove_sparsity(adata) # remove sparsity

logging.info(f'Set up scGEN with parameters:\n{pformat(model_params)}')
model = sca.models.scgen(
    adata=adata,
    **model_params,
)

logging.info(f'Train scGEN with parameters:\n{pformat(train_params)}')
model.train(
    **train_params,
    early_stopping_kwargs={
        "early_stopping_metric": "val_loss",
        "patience": 20,
        "threshold": 0,
        "reduce_lr": True,
        "lr_patience": 13,
        "lr_factor": 0.1,
    },
)

logging.info('Save model...')
model.save(output_model, overwrite=True)

logging.info(adata.__str__())
corrected_adata = model.batch_removal(
    adata,
    batch_key=batch_key,
    cell_label_key=label_key,
    return_latent=True,
)

# prepare output adata
adata.X = corrected_adata.X
adata.obsm["X_emb"] = corrected_adata.obsm["latent_corrected"]
adata = remove_slots(adata=adata, output_type=params['output_type'], keep_X=True)
add_metadata(
    adata,
    wildcards,
    params,
    model_history=dict(model.trainer.logs)
)

logging.info(adata.__str__())
logging.info(f'Write {output_file}...')
write_zarr_linked(
    adata,
    input_file,
    output_file,
    files_to_keep=['X', 'obsm', 'var', 'varm', 'varp', 'uns']
)