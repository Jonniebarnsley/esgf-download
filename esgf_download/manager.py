import os
from itertools import product
from pyesgf.search import SearchConnection # type: ignore

from esgf_download.classes import Dataset
from esgf_download.login import login_to_esgf
from esgf_download.download import download_dataset
from esgf_download.search import (
    search_dataset, filter_2300_extensions, get_latest_result,
    should_filter_2300_extensions, build_query
)

from esgf_download.console import console


class DownloadManager:
    """Manages the ESGF download process."""
    
    def __init__(self, config):
        """
        Initialize the download manager.
        
        Parameters
        ----------
        config : object
            Configuration object with all necessary settings
        """
        self.config = config
        self.conn = None
        
    def setup(self):
        """Logs into ESGF, sets environment variables, and creates a search connection."""
        # Suppress warnings about missing facets
        os.environ['ESGF_PYCLIENT_NO_FACETS_STAR_WARNING'] = 'true'
        
        # Login to ESGF
        try:
            login_to_esgf(self.config.USERNAME, self.config.PASSWORD, self.config.MYPROXY_HOST)
        except Exception as e:
            console.print(f"[red]✗ ESGF login failed:[/red] {e}")
            return False
            
        # Create search connection
        self.conn = SearchConnection(self.config.SEARCH_NODE, distrib=True)
        console.print(f"[blue]📁 Downloading data to[/blue] [bold]{self.config.DATA_HOME}[/bold]")
        return True
    
    def fetch_dataset(self, scenario: str, model: str, variable: str):
        """
        Fetch a dataset for the given scenario, model, and variable combination.
        
        Parameters
        ----------
        scenario : str
            Climate scenario
        model : str
            Climate model
        variable : str
            Climate variable
            
        Returns
        -------
        Dataset | None
            Dataset object if found, None if not found or filtered out
        """
        if self.conn is None:
            console.print("[red]✗ No search connection available[/red]")
            return None
            
        query = build_query(self.config, scenario, model, variable)
        results = search_dataset(self.conn, query)

        if results is None:
            console.print(f"[yellow]⚠ No datasets found for[/yellow] [dim]{scenario}, {model}, {variable}[/dim]")
            return None
        
        # Filter for 2300 extensions if enabled
        if should_filter_2300_extensions(scenario, self.config):
            results = filter_2300_extensions(results, self.config)
            if len(results) == 0:
                console.print(f"[yellow]⚠ No 2300 extensions found for[/yellow] [dim]{scenario}, {model}, {variable}[/dim]")
                return None
        
        # Get the most recent version
        latest_result = get_latest_result(results)
        return Dataset(latest_result, data_home=self.config.DATA_HOME)
    
    def run(self):
        """Run the complete download process."""
        if not self.setup():
            return
            
        # Process all combinations
        for scenario, model, variable in product(self.config.SCENARIOS, self.config.MODELS, self.config.VARIABLES):
            # Fetch the dataset
            dataset = self.fetch_dataset(scenario, model, variable)
            if dataset is None:
                continue

            # Check if dataset is empty
            if dataset.is_empty():
                console.print(f"[yellow]⚠ No files found for[/yellow] [dim]{dataset.dataset_id}[/dim]")
                continue
                
            # Check if dataset already exists
            id, node = dataset.dataset_id.split('|')
            if dataset.exists():
                console.print(f"[green]✓ {id}[/green] [dim](already exists)[/dim]")
                continue

            # Download the dataset
            console.print(dataset.dataset_id)
            interrupt = download_dataset(dataset, self.config.MAX_WORKERS)
            if interrupt:
                break 