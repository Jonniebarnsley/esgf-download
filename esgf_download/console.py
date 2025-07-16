"""
Shared rich console instance for consistent formatting throughout the package.
"""

from rich.console import Console

# Shared rich console instance for consistent formatting
console = Console()

MAX_DISPLAY_ROWS = 40 # max number of rows to display in progress bar