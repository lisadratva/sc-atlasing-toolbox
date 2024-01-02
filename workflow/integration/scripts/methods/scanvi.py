import scvi
from pprint import pformat
import logging
logging.basicConfig(level=logging.INFO)

from utils import add_metadata, get_hyperparams, remove_slots, set_model_history_dtypes
from utils_pipeline.io import read_anndata, write_zarr_linked

input_file = snakemake.input[0]
output_file = snakemake.output[0]
output_model = snakemake.output.model
wildcards = snakemake.wildcards
params = snakemake.params
batch_key = wildcards.batch
label_key = wildcards.label

model_params, train_params = get_hyperparams(
    hyperparams=params.get('hyperparams', {}),
    train_params=[
        'max_epochs',
        'observed_lib_size',
        'n_samples_per_label',
        'batch_size',
        'early_stopping'
    ],
)
logging.info(
    f'model parameters:\n{pformat(model_params)}\n'
    f'training parameters:\n{pformat(train_params)}'
)

logging.info(f'Read {input_file}...')
adata = read_anndata(
    input_file,
    X='layers/raw_counts',
    var='var',
    obs='obs',
    uns='uns',
)

# prepare data for model
adata.obs[label_key] = adata.obs[label_key].astype(str).astype('category')

scvi.model.SCVI.setup_anndata(
    adata,
    # categorical_covariate_keys=[batch], # Does not work with scArches
    batch_key=batch_key,
)

logging.info(f'Set up scVI with parameters:\n{pformat(model_params)}')
model = scvi.model.SCVI(
    adata,
    **model_params
)

logging.info(f'Train scVI with parameters:\n{pformat(train_params)}')
model.train(**train_params)

logging.info(f'Set up scANVI on top of scVI with parameters:\n{pformat(model_params)}')
model = scvi.model.SCANVI.from_scvi_model(
    model,
    labels_key=label_key,
    unlabeled_category='nan',
    **model_params
)

logging.info(f'Train scANVI with parameters:\n{pformat(train_params)}')
model.train(**train_params)

logging.info('Save model...')
model.save(output_model, overwrite=True)

# prepare output adata
adata.obsm["X_emb"] = model.get_latent_representation()
adata = remove_slots(adata=adata, output_type=params['output_type'], keep_X=True)
add_metadata(
    adata,
    wildcards,
    params,
    model_history=set_model_history_dtypes(model.history)
)

logging.info(f'Write {output_file}...')
logging.info(adata.__str__())
write_zarr_linked(
    adata,
    input_file,
    output_file,
    files_to_keep=['obsm', 'uns'],
)