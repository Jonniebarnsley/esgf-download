"""
Configuration file for ESGF download tool.

This file contains all configurable parameters for downloading climate model data
from the Earth System Grid Federation (ESGF).
"""

import os
from pathlib import Path

# --- Authentication Configuration ---

# Ensure that these environment variables are set, e.g. in your .bashrc
USERNAME = os.environ.get('ESGF_USERNAME')
PASSWORD = os.environ.get('ESGF_PASSWORD')
DATA_PATH = Path(os.environ.get('DATA_HOME', './'))  # Default to current directory if not set

# --- ESGF Node Configuration ---

# ESGF node to log into
MYPROXY_HOST = 'esgf-node.ipsl.upmc.fr'

'''
N.B. Login to ESGF can be very temperamental. If you're having issues, try creating an
account on one of the other ESGF nodes, such as:

    esgf.ceda.ac.uk
    esgf-data.dkrz.de
    esgf-node.ipsl.upmc.fr

And setting this as MYPROXY_HOST with the correct username and password (username and password
may differ between nodes). Logging in this way will still allow you to access data from all
ESGF nodes. You should still download from the node geographically closest to you for speed. 
'''

SEARCH_NODE = 'http://esgf-node.ipsl.upmc.fr/esg-search'

# You should ideally set this to the ESGF node geographically closest to you
DATA_NODE_PREFERENCE = 'esgf.ceda.ac.uk'

# --- Data Selection Configuration ---

PROJECT = 'CMIP6'
FREQUENCY = 'mon'   # monthly 
GRID_LABEL = 'gn'   # gn - native grid, gr - regridded to lat-lon

SCENARIOS = ['ssp126']  # ['historical', 'ssp126', 'ssp585']
VARIABLES = ['tas', 'pr', 'evspsbl', 'mrro', 'thetao', 'so']
MODELS = ['CESM2-WACCM', 'IPSL-CM6A-LR', 'MRI-ESM2-0', 'ACCESS-ESM1-5',  
          'CanESM5', 'CNRM-ESM2-1', 'MIROC-ES2L']  # ACCESS-CM2, UKESM1-0-LL

# --- Variable to Table ID Mapping ---

TABLE_ID = {
    'tas': 'Amon',
    'pr': 'Amon',
    'evspsbl': 'Amon',
    'mrro': 'Lmon',
    'thetao': 'Omon',
    'so': 'Omon'
}

# --- Model Variant Labels ---

# UKESM1-0-LL has a different variant label to most models
VARIANT_LABEL = {model: 'r4i1p1f2' if model == 'UKESM1-0-LL' else 'r1i1p1f1' for model in MODELS} 