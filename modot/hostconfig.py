'''Object for parsing and containing the host configuration.'''
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class HostConfig():
    '''Stores values parsed from the host configuration.'''
    themes_path: Path
    colors_path: Path
    domains: List[Path] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)


def from_file(host_path: Path) -> HostConfig:
    '''Gets a host configuration from the file at the given path.'''
    raise NotImplementedError
