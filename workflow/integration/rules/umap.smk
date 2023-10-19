######### UMAP and embedding plots #########

use rule umap from preprocessing as integration_compute_umap with:
    input:
        anndata=rules.integration_postprocess.output.zarr,
        rep=lambda wildcards: mcfg.get_input_file(wildcards.dataset, wildcards.file_id)
    output:
        zarr=directory(out_dir / paramspace.wildcard_pattern / 'umap.zarr'),
    params:
        neighbors_key=lambda w: [
            f'neighbors_{output_type}' for output_type
            in mcfg.get_from_parameters(w, 'output_type')
        ],
    resources:
        partition=mcfg.get_resource(profile='gpu',resource_key='partition'),
        qos=mcfg.get_resource(profile='gpu',resource_key='qos'),
        mem_mb=mcfg.get_resource(profile='gpu',resource_key='mem_mb'),
        gpu=mcfg.get_resource(profile='gpu',resource_key='gpu'),


def get_colors(wildcards):
    dataset = wildcards.dataset
    labels = mcfg.get_from_parameters(wildcards, 'label')
    labels = labels if isinstance(labels, list) else [labels]
    batch = mcfg.get_from_parameters(wildcards, 'batch')
    batch = batch if isinstance(batch, list) else [batch]
    umap_colors = mcfg.get_for_dataset(dataset, query=[mcfg.module_name, 'umap_colors'], default=[])
    return [*labels, *batch, *umap_colors]


use rule plot_umap from preprocessing as integration_plot_umap with:
    input:
        anndata=rules.integration_compute_umap.output.zarr,
    output:
        plot=image_dir / 'umap' / f'{paramspace.wildcard_pattern}.png',
        additional_plots=directory(image_dir / 'umap' / paramspace.wildcard_pattern),
    params:
        color=get_colors,
        ncols=1,
        neighbors_key=lambda w: [
            f'neighbors_{output_type}' for output_type
            in mcfg.get_from_parameters(w, 'output_type')],
        outlier_factor=10,
    resources:
        partition=mcfg.get_resource(profile='cpu',resource_key='partition'),
        qos=mcfg.get_resource(profile='cpu',resource_key='qos'),
        mem_mb=mcfg.get_resource(profile='cpu',resource_key='mem_mb'),
        gpu=mcfg.get_resource(profile='cpu',resource_key='gpu'),


rule plots_all:
    input:
        rules.benchmark_all.input,
        mcfg.get_output_files(rules.integration_plot_umap.output),
