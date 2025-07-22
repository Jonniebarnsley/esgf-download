from pyesgf.search import SearchConnection # type: ignore
from esgf_download.classes import Dataset


def build_query(config, scenario: str, model: str, variable: str) -> dict:
    """Build a search query dictionary for ESGF search."""
    return {
        'project': config.PROJECT,
        'source_id': model,
        'variant_label': config.VARIANT_LABEL[model],
        'experiment_id': scenario,
        'variable': variable,
        'table_id': config.TABLE_ID[variable],
        'frequency': config.FREQUENCY,
        'data_node': config.DATA_NODE_PREFERENCE,
        'grid_label': config.GRID_LABEL[variable],
        'latest': True,
    }
    
def search_dataset(conn: SearchConnection, query: dict):
    """
    Search for datasets with optional data node preference. If no results
    are found, try without data node preference.
    
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

def should_filter_2300_extensions(scenario: str, config) -> bool:
    """Check if 2300 extensions should be filtered for a given scenario."""
    scenarios_to_2300 = ['ssp126', 'ssp585', 'ssp534-over']
    return config.EXTENSIONS_2300 and scenario in scenarios_to_2300

def filter_2300_extensions(results, config) -> list:
    """
    Filters a list of results to only include datasets that end in the year 2299 or 2300
    
    Parameters
    ----------
    results : list
        List of search results
    config : object
        Configuration object
        
    Returns
    -------
    list
        Filtered list of results
    """
    assert config.EXTENSIONS_2300, "2300_extensions flag not enabled - something has gone wrong"
    filtered_results = []
    for result in results:
        dataset = Dataset(result, config.DATA_HOME)
        if dataset.end_date is None:
            # if dataset json has no end date, try to get the end date from the files
            last_file = dataset.files[-1]
            if last_file.end_date.year >= 2299:
                filtered_results.append(result)
            continue
        elif dataset.end_date.year >= 2299:
            filtered_results.append(result)

    return filtered_results


def get_latest_result(results):
    """Get the most recent version of a dataset from search results."""
    return sorted(results, key=lambda r: r.json['version'], reverse=True)[0]

