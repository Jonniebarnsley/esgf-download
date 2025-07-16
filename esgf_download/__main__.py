import os
import argparse
from itertools import product
from pyesgf.search import SearchConnection # type: ignore

# local imports
from esgf_download.classes import Dataset
from esgf_download.login import login_to_esgf
from esgf_download.download import download_dataset
from esgf_download.parser import load_config
from esgf_download.console import console


def search_dataset(conn: SearchConnection, query: dict):
    """
    Search for datasets with optional data node preference.
    
    Parameters
    ----------
    conn : SearchConnection
        ESGF search connection
    query : dict
        Query parameters
        
    Returns
    -------
    ResultSet | None
        Search results
    """
    # First try with data node preference
    context = conn.new_context(**query, facets=query.keys())
    
    if context.hit_count and context.hit_count > 0:
        return context.search()
    
    # If no results and we have a data node preference, try without it
    if 'data_node' in query:
        query.pop('data_node')
        return search_dataset(conn, query)
    
    # No datasets found
    return None

def filter_2300_extensions(results, config) -> list:

    assert config.EXTENSIONS_2300, "2300_extensions flag not enabled - something has gone wrong"
    filtered_results = []
    for result in results:
        dataset = Dataset(result, config.DATA_HOME)
        if dataset.end_date in ['229912', '230012']:
            filtered_results.append(result)

    return filtered_results

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

        results = search_dataset(conn, query)

        if results is None:
            console.print(f"[yellow]⚠ No datasets found for[/yellow] [dim]{scenario}, {model}, {variable}[/dim]")
            continue
        
        # filter for 2300 extensions if enabled
        scenarios_to_2300 = ['ssp126', 'ssp585', 'ssp534-over']
        if config.EXTENSIONS_2300 and scenario in scenarios_to_2300:
            results = filter_2300_extensions(results, config)
            # if no 2300 extensions found, skip
            if len(results) == 0:
                console.print(f"[yellow]⚠ No 2300 extensions found for[/yellow] [dim]{scenario}, {model}, {variable}[/dim]")
                continue
        
        # sort results by most recent version
        results_by_version = sorted(results, key=lambda r: r.json['version'], reverse=True)
        latest_result = results_by_version[0]
        dataset = Dataset(latest_result, config.DATA_HOME) # most recent dataset version

        id, node = dataset.dataset_id.split('|')
        if all(file.exists() for file in dataset.files):
            console.print(f"[green]✓ {id}[/green] [dim](already exists)[/dim]")
            continue
        
        console.print(dataset.dataset_id)
        interrupt = download_dataset(dataset, config.MAX_WORKERS)
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