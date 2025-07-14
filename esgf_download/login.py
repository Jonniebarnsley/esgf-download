import ssl
from typing import Optional
from pyesgf.logon import LogonManager # type: ignore

# local imports
from esgf_download.console import console


def login_to_esgf(username: Optional[str], password: Optional[str], hostname: str) -> None:
    """
    Handles ESGF login and SSL certificate setup for authenticated access.

    This function logs into the specified ESGF node using MyProxy credentials
    and sets up the SSL context required for downloading data from ESGF servers.

    Parameters
    ----------
    username : Optional[str]
        ESGF username for authentication (from environment variable)
    password : Optional[str]  
        ESGF password for authentication (from environment variable)
    hostname : str
        ESGF node hostname for login (e.g., 'esgf-node.ipsl.upmc.fr')

    Raises
    ------
    ValueError
        If username or password are None (environment variables not set)
    Exception
        If login fails or SSL setup encounters errors
    """
    if not username or not password:
        console.print("[red]✗ Error:[/red] ESGF_USERNAME and ESGF_PASSWORD environment variables must be set")
        raise ValueError("ESGF credentials not found in environment variables")
    
    lm = LogonManager()
    lm.logon(username=username, password=password, hostname=hostname)
    
    console.print(f"[green]✓ Successfully logged into ESGF node:[/green] [bold]{hostname}[/bold]")
    
    # Set up SSL context for secure downloads
    sslcontext = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    sslcontext.load_verify_locations(capath=lm.esgf_certs_dir)
    sslcontext.load_cert_chain(lm.esgf_credentials)