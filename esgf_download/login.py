from pyesgf.logon import LogonManager # type: ignore

def login_to_esgf(username, password, hostname) -> None:
    
    """
    Authenticates the user with the ESGF node using the provided username, password, and hostname.
    Sets up the SSL context for secure data access. Raises a ValueError if credentials are missing.
    Prints a success message upon successful login. Returns the SSL context.

    Parameters
    ----------

    username : str
        ESGF account username.
    password : str
        ESGF account password.
    hostname : str
        ESGF node hostname to log into.
    """

    if not username or not password:
        raise ValueError("ESGF_USERNAME and ESGF_PASSWORD environment variables must be set.")
    
    lm = LogonManager()
    if not lm.is_logged_on():
        lm.logon(username=username, password=password, hostname=hostname)
        print(f"Successfully logged into ESGF node: {hostname}")

    # old: ssl context for asyncio implementation – may come back to this
    # sslcontext = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    # sslcontext.load_verify_locations(capath=lm.esgf_certs_dir)
    # sslcontext.load_cert_chain(lm.esgf_credentials)