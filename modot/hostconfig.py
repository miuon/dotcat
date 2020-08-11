'''Object for parsing and containing the host configuration.'''
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


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
    with open(host_path, 'r') as stream:
        host_dict = yaml.safe_load(stream)
    host_cfg = HostConfig(
        Path(host_dict['themes']).expanduser(),
        Path(host_dict['colors']).expanduser())
    host_cfg.default_theme = host_dict.get('default_theme')
    host_cfg.default_color = host_dict.get('default_color')
    host_cfg.domains = [
        Path(dom).expanduser() for dom in host_dict.get('domains', [])]
    host_cfg.modules = host_dict.get('modules', [])
    return host_cfg


def get_deployed_host(active_host_path) -> Optional[Path]:
    '''Returns the path to the deployed host, if there is one.'''
    if active_host_path.exists():
        if not active_host_path.is_symlink():
            raise FileExistsError
        return active_host_path.resolve()
    else:
        return None
