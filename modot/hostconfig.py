'''Object for parsing and containing the host configuration.'''
from pathlib import Path


class HostConfig():
    '''Parses the host configuration and provides values from it.'''
    def __init__(self, host_path: Path):
        '''Populate the host config from the file at the given path.'''
