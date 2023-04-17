# ESGF tools

This is a codebase of helpful tools to work with the Earth System Grid Federation's (ESGF) data archive using Python. It makes heavy use of the package `pyesgf`, but expands its functionality to include asyncronous downloading of files using `aiohttp`. The jupyter notebook `download_tutorial.ipynb` runs through some simple code to explore the ESGF archive and download datasets. Alternatively, the script `download.py` can be configured to download multiple datasets by editing the query in the first few lines. This can then be run from the command line for ease of use.

## Setup

Requires conda & git.

- Clone the repositry directly from github:

        $ git clone https://github.com/Jonniebarnsley/ESGF
        $ cd ESGF

- Create new conda environment with all required dependencies using environment.yml

        $ conda env create -f environment.yml
        $ conda activate esgf
    
- Create an ESGF account with the [German Climate Computing Centre](https://esgf-data.dkrz.de/user/add/?next=http://esgf-data.dkrz.de/projects/esgf-dkrz/).
- CORDEX datasets first require registration to gain access. Apply for CORDEX access [here](https://esg-dn1.nsc.liu.se/ac/subscribe/CORDEX_Research) - for some reason, you may need to repeat this process more than once before access is granted.

- Set some environment variables for your ESGF username, password, and the directory in which you want to store your climate model data:

        $ export ESGF_USERNAME=some_username
        $ export ESGF_PASSWORD=some_password
        $ export DATA_HOME=/path/to/data

Or add equivalent lines to your shell configuration file (such as `.bashrc` or `.zshrc`) followed by (for example):

        $ source ~/.bashrc

or

        $ source ~/.zshrc

You are now ready to explore the `download_tutorial.ipynb` notebook. Alternatively, edit `download.py` in a text editor of your choice and run it from the command line using:

        $ python download.py