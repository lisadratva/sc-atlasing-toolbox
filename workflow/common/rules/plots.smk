from utils.wildcards import wildcards_to_str
from utils.environments import get_env


rule dotplot:
    input: anndata='{filename}.h5ad'
    output:
        plot='{filename}_dotplot.png'
    params:
        var_names=[
            'TNFRSF4', 'SSU72', 'PARK7', 'RBP7', 'SRM',
            'MAD2L2', 'AGTRAP', 'TNFRSF1B', 'EFHD2'
        ],
        groupby='louvain',
        use_raw=False,
        standard_scale='var',
        dendrogram=False,
        swap_axes=False,
    conda:
        get_env(config, 'scanpy')
    script:
        '../scripts/dotplot.py'


rule embedding:
    input:
        anndata='{filename}.h5ad'
    output:
        plot='{filename}_embedding.png'
    params:
        color='bulk_labels',
        basis='X_pca',
    conda:
        get_env(config, 'scanpy')
    script:
        '../scripts/embedding.py'


rule umap:
    input:
        anndata='{filename}.h5ad'
    output:
        plot='{filename}_umap.png',
        coordinates='{filename}_coordinates.npy',
    params:
        color='bulk_labels',
        use_rep='X_pca',
    conda:
        get_env(config, 'scanpy', gpu_env='scanpy_rapids')
    script:
        '../scripts/umap.py'


rule barplot:
    input:
        tsv='test/data/integration.benchmark.tsv'
    output:
        png='{out_dir}/barplot_{metric}.png',
    params:
        metric=lambda wildcards: wildcards.metric,
        category='method',
        hue=None,
        facet_row='dataset',
        facet_col=None,
        title='Barplot',
        description=wildcards_to_str,
        dodge=True,
        xlim=(-.01, None),
    conda:
        get_env(config, 'plots')
    localrule: True
    script:
        '../scripts/barplot.py'


rule swarmplot:
    input:
        tsv='test/data/metrics.tsv'
    output:
        png='{out_dir}/swarmplot_{metric}.png',
    params:
        metric=lambda wildcards: wildcards.metric,
        category='metric',
        hue='method',
        title='Swarmplot',
        description=wildcards_to_str,
        ylim=(-.05, 1.05),
    conda:
        get_env(config, 'plots')
    localrule: True
    script:
        '../scripts/swarmplot.py'
