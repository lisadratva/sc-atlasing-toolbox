import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import scanpy as sc

sns.set_theme(style='white')


def plot_qc_joint(
        adata,
        x,
        y,
        log=1,
        hue=None,
        marginal_hue=None,
        marginal_legend=False,
        palette=None,
        x_threshold=(0, np.inf),
        y_threshold=(0, np.inf),
        title=''
):
    """
    Plot scatter plot with marginal histograms from obs columns in anndata object.

    :param adata: anndata object
    :param x: obs column for x axis
    :param y: obs column for y axis
    :param log: log base for transforming values. Default 1, no transformation
    :param hue: obs column with annotations for color coding scatter plot points
    :param marginal_hue: obs column with annotations for color coding marginal plot distributions
    :param palette: a matplotlib colormap for scatterplot points
    :param x_threshold: tuple of upper and lower filter thresholds for x axis
    :param y_threshold: tuple of upper and lower filter thresholds for y axis
    :param title: Title text for plot
    """

    adata = adata.copy()

    def log1p_base(_x, base):
        return np.log1p(_x) / np.log(base)

    if log > 1:
        x_log = f'log1p_{x}'
        y_log = f'log1p_{y}'
        adata.obs[x_log] = log1p_base(adata.obs[x], log)
        adata.obs[y_log] = log1p_base(adata.obs[y], log)
        x_threshold = log1p_base(x_threshold, log)
        y_threshold = log1p_base(y_threshold, log)
        x = x_log
        y = y_log

    g = sns.JointGrid(data=adata.obs, x=x, y=y)
    # main plot
    g.plot_joint(
        sns.scatterplot,
        data=adata[adata.obs.sample(adata.n_obs).index].obs,
        alpha=.3,
        hue=hue,
        s=2,
        palette=palette,
    )
    # marginal hist plot
    use_marg_hue = marginal_hue is not None
    g.plot_marginals(
        sns.histplot,
        data=adata.obs,
        hue=marginal_hue,
        legend=marginal_legend,
        element='step' if use_marg_hue else 'bars',
        fill=False,
        bins=100
    )

    g.fig.suptitle(title)

    # x threshold
    for t, t_def in zip(x_threshold, (0, np.inf)):
        if t != t_def:
            g.ax_joint.axhline(y=t, color='red')
            g.ax_marg_y.axhline(y=t, color='red')

    # y threshold
    for t, t_def in zip(y_threshold, (0, np.inf)):
        if t != t_def:
            g.ax_joint.axvline(x=t, color='red')
            g.ax_marg_x.axvline(x=t, color='red')

    return g


sc.set_figure_params(frameon=False)

input_h5ad = snakemake.input.h5ad
output_joint = snakemake.output.joint
output_umi = snakemake.output.umi
dataset = snakemake.wildcards.dataset

adata = sc.read(input_h5ad)

adata.var["mito"] = adata.var['feature_name'].str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mito"], inplace=True)

plt.rcParams['figure.figsize'] = 12, 12
plot_qc_joint(
    adata,
    x='total_counts',
    y='n_genes_by_counts',
    hue='pct_counts_mito',
    palette='plasma',
    title=f'Joint QC for {dataset}',
)
plt.tight_layout()
plt.savefig(output_joint)

plt.rcParams['figure.figsize'] = 22, 6
g = sns.boxplot(x="sample", y="total_counts", data=adata.obs, hue='pct_counts_mito')
g.set_xticklabels(g.get_xticklabels(), rotation=90)

plt.tight_layout()
plt.savefig(output_umi)
