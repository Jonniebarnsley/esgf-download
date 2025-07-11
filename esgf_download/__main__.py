from itertools import product
from pyesgf.search import SearchConnection # type: ignore
from typing import Optional

# Clean imports now that package is installed
from esgf_download.classes import Dataset
from esgf_download.login import login_to_esgf
from esgf_download.download import download_dataset
from esgf_download.config import load_config


def main(config_path: Optional[str] = None) -> None:
    """
    Main application function.
    
    Parameters
    ----------
    config_path : str, optional
        Path to YAML configuration file. If None, uses default config.yaml.
    """
    # Load configuration
    if config_path is None:
        config_path = "config.yaml"
    config = load_config(config_path)

    try:
        login_to_esgf(config.USERNAME, config.PASSWORD, config.MYPROXY_HOST)
    except Exception as e:
        print(f"ESGF login failed: {e}")
        return

    conn = SearchConnection(config.SEARCH_NODE, distrib=True)
    for scenario, model, variable in product(config.SCENARIOS, config.MODELS, config.VARIABLES):

        query = {
            'project': config.PROJECT,
            'source_id': model,
            'variant_label': config.VARIANT_LABEL[model],
            'experiment_id': scenario,
            'variable': variable,
            'table_id': config.TABLE_ID[variable],
            'frequency': config.FREQUENCY,
            'data_node': config.DATA_NODE_PREFERENCE,
            'grid_label': config.GRID_LABEL,
        }

        context = conn.new_context(**query, facets=query.keys())

        if context.hit_count == 0:
            print(f"No datasets found for {scenario}, {model}, {variable}.")
            continue

        results = context.search()
        dataset = Dataset(list(results)[-1], config.DATA_PATH) # most recent dataset version

        if all(file.exists() for file in dataset.files):
            print(f"All files for {scenario}, {model}, {variable} already exist, skipping download.")
            continue

        interrupt = download_dataset(dataset)
        if interrupt:
            break


if __name__ == "__main__":
    main()