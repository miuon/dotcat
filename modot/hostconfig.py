'''Object for parsing and containing the host configuration.'''
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HostConfig():
    '''Parses the host configuration and provides values from it.'''
    themes_path: Path
    colors_path: Path


def from_file(host_path: Path) -> HostConfig:
    '''Gets a host configuration from the file at the given path.'''
