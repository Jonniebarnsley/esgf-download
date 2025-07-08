# ESGF Download Tool

A Python tool for downloading climate model data from the Earth System Grid Federation (ESGF). This tool provides automated downloading of CMIP6 climate model outputs with configurable parameters for scenarios, models, and variables.

## Overview

The ESGF Download Tool simplifies the process of downloading climate model data from ESGF nodes. It handles authentication, file discovery, and downloading with progress tracking. The tool is specifically configured for CMIP6 data but can be easily modified for other projects.

## Features

- **Automated Authentication**: Handles ESGF login and SSL certificate management
- **Configurable Downloads**: Easy configuration of scenarios, models, variables, and time periods
- **Progress Tracking**: Visual progress bars for file downloads
- **Resume Capability**: Skips already downloaded files
- **Organized File Structure**: Automatically organizes downloaded files in a logical directory structure
- **Multiple ESGF Node Support**: Can download from different ESGF nodes based on geographic proximity

## Prerequisites

### ESGF Account
You need an ESGF account to download data. If you don't have one, you can create an account at any of these ESGF nodes:
- [esgf.ceda.ac.uk](https://esgf.ceda.ac.uk)
- [esgf-data.dkrz.de](https://esgf-data.dkrz.de)
- [esgf-node.ipsl.upmc.fr](https://esgf-node.ipsl.upmc.fr)

### Python Environment
- Python 3.7 or higher
- pip or conda for package management

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd esgf-download
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv pyesgf-env
   source pyesgf-env/bin/activate  # On Windows: pyesgf-env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   export ESGF_USERNAME="your_esgf_username"
   export ESGF_PASSWORD="your_esgf_password"
   export DATA_HOME="/path/to/your/data/directory"
   ```

   Add these to your shell profile (`.bashrc`, `.zshrc`, etc.) for persistence.

## Configuration

The main configuration is in `download.py`. Key parameters you can modify:

### Data Selection
```python
SCENARIOS = ['ssp126']  # ['historical', 'ssp126', 'ssp585']
VARIABLES = ['tas', 'pr', 'evspsbl', 'mrro', 'thetao', 'so']
MODELS = ['CESM2-WACCM', 'IPSL-CM6A-LR', 'MRI-ESM2-0', 'ACCESS-ESM1-5', 
          'CanESM5', 'CNRM-ESM2-1', 'MIROC-ES2L']
```

### Data Specifications
```python
PROJECT = 'CMIP6'
FREQUENCY = 'mon'   # monthly data
GRID_LABEL = 'gn'   # gn - native grid, gr - regridded to lat-lon
```

### ESGF Node Configuration
```python
MYPROXY_HOST = 'esgf-node.ipsl.upmc.fr'  # Login node
SEARCH_NODE = 'http://esgf-node.ipsl.upmc.fr/esg-search'  # Search node
DATA_NODE_PREFERENCE = 'esgf.ceda.ac.uk'  # Download node (choose closest to you)
```

## Usage

### Basic Usage
Run the download script:
```bash
python download.py
```

This will download all configured datasets based on the parameters in the script.

### Interactive Exploration
Use the Jupyter notebook for interactive exploration:
```bash
jupyter notebook explore.ipynb
```

The notebook allows you to:
- Test ESGF connectivity
- Explore available datasets
- Verify download URLs
- Customize queries interactively

## File Organization

Downloaded files are organized in the following structure:
```
<DATA_HOME>/
├── CMIP6/
│   ├── ScenarioMIP/
│   │   ├── <institute>/
│   │   │   ├── <model>/
│   │   │   │   ├── <experiment>/
│   │   │   │   │   ├── <realisation>/
│   │   │   │   │   │   ├── <time_resolution>/
│   │   │   │   │   │   │   ├── <variable>/
│   │   │   │   │   │   │   │   ├── gr/
│   │   │   │   │   │   │   │   │   └── <version>/
│   │   │   │   │   │   │   │   │       └── <files>
```

## Troubleshooting

### Login Issues
ESGF login can be temperamental. If you're having issues:
1. Try a different ESGF node for login
2. Ensure your credentials are correct
3. Check if your account is active

### Download Failures
- Check your internet connection
- Verify the ESGF node is accessible
- Ensure you have sufficient disk space
- Check if the requested data is available

### SSL Certificate Issues
The tool handles SSL certificates automatically, but if you encounter issues:
1. Ensure the `pyesgf` package is properly installed
2. Check that your ESGF credentials are valid
3. Try logging in manually to the ESGF web interface first

## Customization

### Adding New Variables
To download additional variables, add them to the `VARIABLES` list and their corresponding table IDs to `TABLE_ID`:

```python
VARIABLES = ['tas', 'pr', 'evspsbl', 'mrro', 'thetao', 'so', 'new_variable']
TABLE_ID = {
    'tas': 'Amon',
    'pr': 'Amon',
    # ... existing mappings ...
    'new_variable': 'Amon'  # or appropriate table
}
```

### Adding New Models
Add new models to the `MODELS` list and their variant labels to `VARIANT_LABEL`:

```python
MODELS = ['existing_model', 'new_model']
VARIANT_LABEL = {
    'existing_model': 'r1i1p1f1',
    'new_model': 'r1i1p1f1'  # adjust as needed
}
```

### Different Time Frequencies
Change the `FREQUENCY` parameter:
- `'mon'` - monthly
- `'day'` - daily
- `'yr'` - yearly
- `'3hr'` - 3-hourly

## Acknowledgments

This tool builds upon the `pyesgf` library and the ESGF infrastructure. Thanks to the ESGF community for providing access to climate model data. 