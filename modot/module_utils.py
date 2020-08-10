'''Build generators for retrieving modules and rules from filesystem.'''
from pathlib import Path
from typing import Generator, List

import yaml

from modot.hostconfig import HostConfig
from modot.rule import Rule


MODULE_CONF_FILENAME = 'module.yaml'


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


def get_rules(module_path: Path) -> List[Rule]:
    '''Parse the concat rules from a module.'''
    module_conf_path = module_path / MODULE_CONF_FILENAME
    with open(module_conf_path, 'r') as stream:
        module_config = yaml.safe_load(stream)
    rules = []
    for src_str, conf_dict in module_config.items():
        src_path = (module_path/src_str).expanduser()
        out_path = Path(conf_dict['out']).expanduser()
        if conf_dict.get('dir_contents', False):
            for sub_path in src_path.iterdir():
                sub_name = sub_path.name
                rules.append(
                    _rule_from_yaml(sub_path, out_path/sub_name, conf_dict))
        else:
            rules.append(_rule_from_yaml(src_path, out_path, conf_dict))
    return rules


def _rule_from_yaml(src: Path, out: Path, conf_dict: dict) -> Rule:
    return Rule(src, out,
                executable=conf_dict.get('exec', False),
                final=conf_dict.get('final', False),
                force_rewrite=conf_dict.get('force_rewrite', False))


class DuplicateDomainError(Exception):
    '''Raised when a domain has been specified twice.'''
