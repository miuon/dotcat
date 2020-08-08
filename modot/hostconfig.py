'''Object for parsing and containing the host configuration.'''
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class HostConfig():
    '''Stores values parsed from the host configuration.'''
    themes_path: Path
    colors_path: Path
    default_theme: str = ''
    default_color: str = ''
    domains: List[Path] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)


def from_file(host_path: Path) -> HostConfig:
    '''Gets a host configuration from the file at the given path.'''
    raise NotImplementedError


def get_deployed_host(active_host_path) -> Optional[Path]:
    '''Returns the path to the deployed host, if there is one.'''
    if active_host_path.exists():
        if not active_host_path.is_symlink():
            raise FileExistsError
        return active_host_path.resolve()
    else:
        return None
