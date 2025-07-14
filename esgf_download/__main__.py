import argparse
from itertools import product
from pyesgf.search import SearchConnection # type: ignore

# local imports
from esgf_download.classes import Dataset
from esgf_download.login import login_to_esgf
from esgf_download.download import download_dataset
from esgf_download.parser import load_config
from esgf_download.console import console


def main(config_path: str) -> None:
    """
    Main application function.
    
    Parameters
    ----------
    config_path : str, optional
        Path to YAML configuration file.
    """

    # Load configuration
    config = load_config(config_path)

    try:
        login_to_esgf(config.USERNAME, config.PASSWORD, config.MYPROXY_HOST)
    except Exception as e:
        console.print(f"[red]✗ ESGF login failed:[/red] {e}")
        return

    conn = SearchConnection(config.SEARCH_NODE, distrib=True)
    console.print(f"[blue]📁 Downloading data to[/blue] [bold]{config.DATA_HOME}[/bold]")
    
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
            'grid_label': config.GRID_LABEL[model],
        }

        context = conn.new_context(**query, facets=query.keys())

        if context.hit_count == 0:
            console.print(f"[yellow]⚠ No datasets found for[/yellow] [dim]{scenario}, {model}, {variable}[/dim]")
            continue

        results = context.search()
        dataset = Dataset(list(results)[-1], config.DATA_HOME) # most recent dataset version

        id, node = dataset.dataset_id.split('|')
        if all(file.exists() for file in dataset.files):
            console.print(f"[green]✓ {id}[/green] [dim](already exists)[/dim]")
            continue
        
        console.print(f"[bold]{dataset.dataset_id}[/bold]")
        interrupt = download_dataset(dataset)
        if interrupt:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download climate model data from ESGF",
        prog="python -m esgf_download"
    )
    parser.add_argument(
        "config", 
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    main(args.config)