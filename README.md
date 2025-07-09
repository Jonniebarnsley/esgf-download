# ESGF Download

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python tool for downloading climate model data from the Earth System Grid Federation (ESGF). This tool provides automated downloading of CMIP6 climate model outputs with configurable parameters for scenarios, models, and variables. The tool is specifically configured for CMIP6 data but can be easily modified for other projects.

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

The configuration is stored in `config.py`. Key parameters you can modify:

### Data Selection
```python
PROJECT = 'CMIP6'
SCENARIOS = ['historical', 'ssp126']
VARIABLES = ['tas', 'pr', 'evspsbl', 'mrro']
MODELS = ['CESM2-WACCM', 'MRI-ESM2-0', 'ACCESS-ESM1-5']
```
Naming conventions follow ESGF standards – it's recommended that you browse the [ESGF web search tool](https://esgf-metagrid.cloud.dkrz.de/search) before specifying new parameters here. See [Customisation](#customisation) for further details.

### Data Specifications
```python
FREQUENCY = 'mon'   # time resolution of data, mon - monthly. Also 3hr, day, yr
GRID_LABEL = 'gn'   # gn - native grid, gr - regridded to lat-lon
```

### ESGF Node Configuration
```python
MYPROXY_HOST = 'esgf-node.ipsl.upmc.fr'  # Login node
SEARCH_NODE = 'http://esgf-node.ipsl.upmc.fr/esg-search'  # Search node
DATA_NODE_PREFERENCE = 'esgf.ceda.ac.uk'  # Download node (geographically closest to you)
```

N.B. Your login details stored as environment variables must correspond to the login node specified here. It is possible to have accounts with each login node, possibly with different usernames and passwords.

## Usage

### Basic Usage
Run the download script:
```bash
python download.py
```

This will download all configured datasets based on the parameters in the script.

### Interactive Exploration
Use the Jupyter notebook `explore.ipynb` to explore available datasets before specifying them in `download.py`.


The notebook allows you to:
- Test ESGF connectivity
- Explore available datasets
- Verify download URLs
- Customize queries interactively

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

## Troubleshooting

### Login Issues
ESGF login can be temperamental. If you're having issues:
1. Try a different ESGF node for login
2. Ensure your credentials are correct

### Download Failures
Use `explore.ipynb` to:
- Verify the ESGF node is accessible
- Check that a dataset is available

## Customisation

All customization should be done in `config.py`. Here are the main areas you can modify:

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

Table IDs correspond to the earth system component which the variable originates from:
- `Amon`: atmosphere,
- `Omon`: ocean,
- `Lmon`: land surface.

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
