"""
ESGF Download Package

A Python package for downloading climate model data from the Earth System Grid Federation (ESGF).
"""

__version__ = "1.0.0"

from .classes import Dataset, File
from .login import login_to_esgf
from .download import download_dataset

__all__ = ["Dataset", "File", "login_to_esgf", "download_dataset"]