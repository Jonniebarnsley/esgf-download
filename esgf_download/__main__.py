import argparse
from esgf_download.parser import load_config
from esgf_download.manager import DownloadManager


def main(config_path: str) -> None:
    """
    Main application function.
    
    Parameters
    ----------
    config_path : str
        Path to YAML configuration file.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Create and run download manager
    manager = DownloadManager(config)
    manager.run()


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