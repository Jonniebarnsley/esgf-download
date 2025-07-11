# ESGF Download

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python package for downloading climate model data from the Earth System Grid Federation (ESGF). Provides automated, parallel downloading of CMIP6 climate model outputs with configurable parameters for scenarios, models, and variables.

## Prerequisites

### ESGF Account
You need an ESGF account to download data. If you don't have one, you can create an account at any of these ESGF nodes:
- [esgf.ceda.ac.uk](https://esgf-ui.ceda.ac.uk/cog/projects/esgf-ceda/)
- [esgf-data.dkrz.de](https://esgf-metagrid.cloud.dkrz.de/search)
- [esgf-node.ipsl.upmc.fr](https://esgf-node.ipsl.upmc.fr)  

### Python Environment
- Python 3.7 or higher
- pip for package management

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jonniebarnsley/esgf-download.git
   cd esgf-download
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv pyesgf-env
   source pyesgf-env/bin/activate  # On Windows: pyesgf-env\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   export ESGF_USERNAME="your_esgf_username"
   export ESGF_PASSWORD="your_esgf_password"
   export DATA_HOME="/path/to/your/data/directory"
   ```

   Add these to your shell profile (`.bashrc`, `.zshrc`, etc.) for persistence.

## Configuration

The configuration is stored in `config.yaml`. Key parameters you can modify:

```yaml
# ESGF Node Configuration

esgf:
  myproxy_host: "esgf-node.ipsl.upmc.fr"
  search_node: "http://esgf-data.dkrz.de/esg-search"
  data_node_preference: "esgf.ceda.ac.uk"

# Data Selection Configuration
data:
  project: "CMIP6"
  frequency: "mon"        # monthly
  grid_label: "gn"        # gn - native grid, gr - regridded to lat-lon
  
  scenarios:
    - "historical"
    - "ssp126"
    - "ssp585"
  
  variables:
    - "tas"
    - "pr"
    - "evspsbl"
    - "mrro"
    - "thetao"
    - "so"
  
  models:
    - "CESM2-WACCM"
    - "IPSL-CM6A-LR"
    - "MRI-ESM2-0"
    - "ACCESS-ESM1-5"
    - "CanESM5"
    - "CNRM-ESM2-1"
    - "MIROC-ES2L"

# Variable to Table ID Mapping
table_mapping:
  tas: "Amon"
  pr: "Amon"
  evspsbl: "Amon"
  mrro: "Lmon"
  thetao: "Omon"
  so: "Omon"

# Model Variant Labels
variant_labels:
  default: "r1i1p1f1"
  UKESM1-0-LL: "r4i1p1f2"
```

Naming conventions follow ESGF standards – it's recommended that you browse the [ESGF web search tool](https://esgf-metagrid.cloud.dkrz.de/search) before specifying new parameters here. See [Customisation](#customisation) for further details.

## Usage

### Command Line Interface
Run the download with a configuration file:
```bash
# Use the default config.yaml
python -m esgf_download config.yaml

# Use a custom configuration file
python -m esgf_download my_custom_config.yaml

# Show help
python -m esgf_download --help

# Show version
python -m esgf_download --version
```

### Creating Custom Configurations
You can create multiple configuration files for different download scenarios:

```bash
# Download historical data
python -m esgf_download config_historical.yaml

# Download future projections
python -m esgf_download config_ssp585.yaml

# Download specific variables only
python -m esgf_download config_temperature_only.yaml
```

### Interactive Exploration
Use the Jupyter notebook `explore.ipynb` to explore available datasets before creating your configuration files.

The notebook allows you to:
- Test ESGF connectivity
- Explore available datasets
- Verify download URLs
- Test configuration parameters interactively

## File Organization

Downloaded files are organized in the following structure:
```
<DATA_HOME>/
├── <project>/
│   ├── <MIP>/
│   │   ├── <institute>/
│   │   │   ├── <model>/
│   │   │   │   ├── <experiment>/
│   │   │   │   │   ├── <realisation>/
│   │   │   │   │   │   ├── <time_resolution>/
│   │   │   │   │   │   │   ├── <variable>/
│   │   │   │   │   │   │   │   ├── <grid_type>/
│   │   │   │   │   │   │   │   │   └── <version>/
│   │   │   │   │   │   │   │   │       └── <files>
```

## Package Structure

```
esgf-download/
├── esgf_download/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # CLI entry point
│   ├── classes.py          # Dataset and File classes
│   ├── config.py           # YAML configuration loader
│   ├── download.py         # Parallel download functionality
│   └── login.py            # ESGF authentication
├── config.yaml             # Default configuration
├── pyproject.toml          # Package metadata
└── README.md               # This file
```

## Troubleshooting

### Login Issues
ESGF login can be temperamental. If you're having issues:
1. Try a different ESGF node for login in your config file
2. Ensure your environment variables are set correctly
3. Check that your credentials work on the ESGF web interface

### Download Failures
- Use `explore.ipynb` to verify dataset availability
- Check network connectivity to the ESGF data nodes
- Try different login, search, or data node preferences in your config

### Configuration Issues
- Validate your YAML syntax using online YAML validators
- Check that all required sections are present in your config file
- Ensure environment variables are set and accessible

## Customisation

### Adding New Variables
Add new variables to the `variables` list and their corresponding table IDs to `table_mapping`:

```yaml
data:
  variables:
    - "tas"
    - "pr"
    - "new_variable"

table_mapping:
  tas: "Amon"
  pr: "Amon"
  new_variable: "Amon"  # or appropriate table
```

Table IDs correspond to earth system components:
- `Amon`: atmosphere (monthly)
- `Omon`: ocean (monthly)  
- `Lmon`: land surface (monthly)

### Adding New Models
Add new models to the `models` list and specify variant labels if needed:

```yaml
data:
  models:
    - "CESM2-WACCM"
    - "NEW-MODEL"

variant_labels:
  default: "r1i1p1f1"
  NEW-MODEL: "r2i1p1f1"  # if different from default
```

### Different Time Frequencies
Change the `frequency` parameter:
- `mon` - monthly
- `day` - daily
- `yr` - yearly
- `3hr` - 3-hourly

## Acknowledgments

This tool builds upon the `pyesgf` library and the ESGF infrastructure. Thanks to the ESGF community for providing access to climate model data. 
