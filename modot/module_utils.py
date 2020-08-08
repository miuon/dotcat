'''Build generators for retrieving modules and rules from filesystem.'''
from pathlib import Path
from typing import Generator

from modot.hostconfig import HostConfig
from modot.rule import Rule


def get_module_paths(host_cfg: HostConfig) -> Generator[Path, None, None]:
    '''Search for modules based on host_cfg and yield them in order.'''
    encountered_domains = set()
    for domain_path in host_cfg.domains:
        if domain_path in encountered_domains:
            raise DuplicateDomainError
        encountered_domains.add(domain_path)
        if not domain_path.exists():
            raise FileNotFoundError
        if not domain_path.is_dir():
            raise NotADirectoryError
        for module in host_cfg.modules:
            module_path = domain_path / module
            if not module_path.exists():
                continue
            if not module_path.is_dir():
                raise NotADirectoryError
            yield module_path


def get_rules(module_path: Path) -> Generator[Rule, None, None]:
    '''Parse the concat rules from a module file.'''
    raise NotImplementedError

class DuplicateDomainError(Exception):
    '''Raised when a domain has been specified twice.'''
