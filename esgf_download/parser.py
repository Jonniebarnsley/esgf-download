"""
Configuration loader for ESGF download tool.
Loads configuration from YAML files.
"""

import os
import yaml
from pathlib import Path


class Config:
    """Configuration class that loads settings from YAML files."""
    
    def __init__(self, config_path: str):

        """
        Initialize configuration from YAML file.
        
        Parameters
        ----------
        config_path : str
            Path to YAML config file.
        """

        self.config_path = Path(config_path)
        self._load_config()
    
    def _load_config(self):

        """Load configuration from YAML file."""

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Process environment variables and create convenient properties
        self._process_config()
    
    def _process_config(self):

        """Process config data and set up convenient properties."""
        
        # Get credentials from environment variables
        self.USERNAME = os.environ.get("ESGF_USERNAME")
        self.PASSWORD = os.environ.get("ESGF_PASSWORD")
        self.DATA_HOME = Path(os.environ.get("DATA_HOME", "./"))
        
        # ESGF settings
        esgf = self._config['esgf']
        self.MYPROXY_HOST = esgf['myproxy_host']
        self.SEARCH_NODE = esgf['search_node']
        self.DATA_NODE_PREFERENCE = esgf['data_node_preference']
        
        # Download settings
        download = self._config['download']
        self.MAX_WORKERS = download['max_workers']
        
        # Data settings
        data = self._config['data']
        self.PROJECT = data['project']
        self.FREQUENCY = data['frequency']
        self.SCENARIOS = data['scenarios']
        self.VARIABLES = data['variables']
        self.MODELS = data['models']
        
        # Mappings
        self.TABLE_ID = self._config['table_mapping']
        
        # Variant labels - create mapping for all models
        variant_config = self._config['variant_labels']
        default_variant = variant_config['default']
        self.VARIANT_LABEL = {}
        for model in self.MODELS:
            self.VARIANT_LABEL[model] = variant_config.get(model, default_variant)
            
        # Grid labels - create mapping for all models
        grid_config = self._config['grid_labels']
        default_grid = grid_config['default']
        self.GRID_LABEL = {}
        for model in self.MODELS:
            self.GRID_LABEL[model] = grid_config.get(model, default_grid)


def load_config(config_path: str) -> Config:

    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str, optional
        Path to YAML config file.
    
    Returns
    -------
    Config
        Configuration object with all settings.
    """

    return Config(config_path) 