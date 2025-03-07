from matplotlib import pyplot as plt
import scanpy as sc
import anndata

sc.set_figure_params(frameon=False)
plt.rcParams['figure.figsize'] = 30, 25
input_file = snakemake.input.zarr
output_png = snakemake.output.png
dataset = snakemake.params.dataset
markers = snakemake.params.markers

adata = anndata.read_zarr(input_file)

# if no cells filtered out, save empty plots
if adata.n_obs == 0:
    plt.savefig(output_png)
    exit()


author_label = 'author_annotation'
ontology_label = 'cell_type'
print(adata)

def process_markers(markers, adata):
    """
    Recursively process the nested markers dictionary to find matching features
    in adata.var based on the 'feature_name' column.
    """
    processed_markers = {}
    
    for key, value in markers.items():
        if isinstance(value, dict):
            # Recursive call if the value is a dictionary
            processed_markers[key] = process_markers(value, adata)
        else:
            # Base case: value is a list of marker genes
            processed_markers[key] = adata.var[adata.var['feature_name'].isin(value)]['feature_name'].to_list()
            
    return processed_markers


def print_marker_lengths(marker_dict, prefix=""):
    """
    Recursively print the lengths of marker lists at each level of the dictionary.
    """
    for key, value in marker_dict.items():
        if isinstance(value, dict):
            print_marker_lengths(value, prefix + key + " -> ")
        else:
            print(f"{prefix}{key}: {len(value)}")

def simplify_processed_markers(nested_dict):
    """
    Flattens and simplifies a nested marker dictionary to create a single-level dictionary
    with categories as keys and marker lists as values.
    """
    simplified_dict = {}
    
    for main_category, subcategories in nested_dict.items():
        for subcategory, markers in subcategories.items():
            # Combine the main category and subcategory into a single top-level category
            category_key = f"{subcategory}"
            simplified_dict[category_key] = markers
            
    return simplified_dict


# match marker genes and var_names
adata.var_names = adata.var['feature_name'].astype(str)

# Process and print the lengths of each marker list
markers = process_markers(markers, adata)
print_marker_lengths(markers)

# Apply the function to create a simplified markers dictionary
markers = simplify_processed_markers(markers)

# print({k: len(v) for k, v in markers.items()})
# markers = {
#     k: adata.var[adata.var['feature_name'].isin(v)].index.to_list()
#     for k, v in markers.items()
# }
# print({k: len(v) for k, v in markers.items()})

fig, axes = plt.subplots(nrows=2, ncols=1)
# check if author labels column is empty
if adata.obs[author_label].nunique() == 0:
    raise ValueError(f'No author labels in adata["{author_label}"]')

sc.pl.dotplot(
    adata,
    markers,
    groupby=author_label,
    use_raw=False,
    standard_scale='var',
    title=f'Marker genes on {dataset} for author cell types, colummn: "{author_label}"',
    show=False,
    ax=axes[0],
)

sc.pl.dotplot(
    adata,
    markers,
    groupby=ontology_label,
    use_raw=False,
    standard_scale='var',
    title=f'Marker genes on {dataset} for ontology cell types, column: "{ontology_label}"',
    show=False,
    ax=axes[1],
)

plt.tight_layout()
plt.savefig(output_png)
