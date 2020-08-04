'''Reading and processing actions for file deployment.'''
from pathlib import Path
import sys
from typing import List
import yaml

import chevron

from modot.constants import (MODULE_CONFIG_FILE, ACTIVE_THEME_PATH,
                             ACTIVE_COLOR_PATH)
from modot.utils import link_atomic


class ThemeEngine():
    '''Reads and executes configurations for file deployment.'''
    def __init__(self, host_path: Path):
        if not host_path or not host_path.is_file():
            sys.exit('No deployed theme; run modot deploy <host_config>')
        with open(host_path, 'r') as stream:
            host_config = yaml.safe_load(stream)

        self.themes_path = Path(host_config['themes']).expanduser()
        self.colors_path = Path(host_config['colors']).expanduser()
        self.default_theme = host_config.get('default_theme', '')
        self.default_color = host_config.get('default_color', '')
        self.template_dict = {}
        self.setup_actions = []
        self.cat_actions = {}

        self._read_modules(
            [Path(domain).expanduser() for domain in
             host_config.get('domains', [])],
            host_config.get('modules', []))

    def _read_modules(self, domains: List[str], modules: List[str]):
        '''Read module.yaml files for chosen modules in chosen domains.'''
        for domain in domains:
            domain_path = Path(domain).expanduser()
            for module_str in modules:
                module_path = domain_path / Path(module_str)
                module_conf_path = module_path / MODULE_CONFIG_FILE
                if module_conf_path.exists():
                    with open(module_conf_path, 'r') as stream:
                        module_config = yaml.safe_load(stream)
                    if module_config is None:
                        module_config = {}
                    for filestr, fileconf in module_config.items():
                        filepath = module_path / Path(filestr)
                        self._read_fileconf(filepath, fileconf)

    def _read_fileconf(self, filepath: Path, fileconf: dict):
        '''Read configuration for a single file deployment rule.'''
        out_str = fileconf.get('out', '')
        if not out_str:
            sys.exit(f'No output specified for {filepath}')
        out_path = Path(out_str).expanduser()
        if fileconf.get('dir_contents', False):
            if not filepath.is_dir():
                sys.exit(f'dir_contents used on non-dir: {filepath}')
            if out_path.exists() and not out_path.is_dir():
                sys.exit(f'{filepath} exists and is not a directory')
            self.setup_actions.append(_MakeDirAction(out_path))
            for src_path in [p for p in filepath.iterdir() if p.is_file()]:
                out_file_path = out_path / src_path.name
                cat_action = self.cat_actions.get(str(out_file_path), None)
                if cat_action:
                    cat_action.add_path(src_path, fileconf)
                else:
                    self.cat_actions[str(out_file_path)] = _CatAction(
                        src_path, out_file_path, fileconf)

        else:
            cat_action = self.cat_actions.get(str(out_path), None)
            if cat_action:
                cat_action.add_path(filepath, fileconf)
            else:
                self.setup_actions.append(_MakeDirAction(out_path.parent))
                self.cat_actions[str(out_path)] = _CatAction(
                    filepath, out_path, fileconf)

    def list_themes(self) -> List[str]:
        '''List the theme options in the configured theme directory.'''
        return [path.stem for path in self.themes_path.iterdir()]

    def list_colors(self) -> List[str]:
        '''List the color options in the configured color directory.'''
        return [path.stem for path in self.colors_path.iterdir()]

    def set_theme(self, name):
        '''Change the deployed theme file by changing the active theme link.'''
        link_atomic(self.themes_path /
                    Path(name).with_suffix('.yaml'), ACTIVE_THEME_PATH)
        if ACTIVE_COLOR_PATH.exists():
            self.read_template_dict()

    def set_color(self, name):
        '''Change the deployed color file by changing the active color link.'''
        link_atomic(self.colors_path /
                    Path(name).with_suffix('.yaml'), ACTIVE_COLOR_PATH)
        if ACTIVE_THEME_PATH.exists():
            self.read_template_dict()

    def read_template_dict(self):
        '''Read the template variables from the theme and color files.'''
        if (not ACTIVE_COLOR_PATH.exists() or
                not ACTIVE_THEME_PATH.exists()):
            sys.exit('Failed to properly set color/theme')
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            color_dict = yaml.safe_load(stream)
        with open(ACTIVE_THEME_PATH, 'r') as stream:
            theme_dict = yaml.safe_load(stream)
        self.template_dict = {**color_dict, **theme_dict}

    def print_actions(self):
        '''Print all actions queued to be taken.'''
        for action in self.setup_actions:
            print(action)
        for action in self.cat_actions.values():
            print(action)

    def deploy(self):
        '''Execute all prepared actions to deploy the configuration.'''
        for action in self.setup_actions:
            action.run()
        for action in self.cat_actions.values():
            action.run(self.template_dict)


class _MakeDirAction():
    '''Action representing intent to make a directory if nonexistent.'''
    def __init__(self, path: Path):
        self.path = path

    def __repr__(self) -> str:
        return f'Create directory: {self.path}'

    def run(self):
        '''Create the configured directory if nonexistent.'''
        if self.path.is_symlink():
            self.path.unlink()
        elif self.path.exists() and not self.path.is_dir():
            sys.exit(f'Found a non-dir at {self.path} while trying to mkdir.')
        self.path.mkdir(parents=True, exist_ok=True)


class _CatAction():
    '''Intent object for concatenation of one or more paths to an output.'''
    def __init__(self, src_path: Path, out_path: Path, options: dict):
        self.src_paths = [src_path]
        self.out_path = out_path
        self.template_dict = {}
        self.executable = options.get('exec', False)
        self.final = options.get('final', False)

    def __repr__(self) -> str:
        return f'Cat: {self.src_paths} -> {self.out_path}'

    def add_path(self, src_path: Path, options: dict):
        '''Add a new source to concatenate to the configured output.'''
        self.src_paths.append(src_path)
        self.executable = self.executable or options.get('exec', False)
        self.final = self.final or options.get('final', False)

    def run(self, template_dict: dict):
        '''Execute the concatenation if it would change the outfile.'''
        self.template_dict = template_dict
        if self.final and len(self.src_paths) > 1:
            sys.exit(f'Multiple rules writing to final path {self.out_path}')
        if self.out_path.is_dir():
            sys.exit(f'Target {self.out_path} is a directory, please delete')
        if self.out_path.is_symlink():
            self.out_path.unlink()
        if not self._files_equal():
            self._write_files()

    def _files_equal(self) -> bool:
        if not self.out_path.is_file():
            return False
        with open(self.out_path, 'r') as out_file:
            rendered_str = ''
            for src_path in self.src_paths:
                with open(src_path, 'r') as src_file:
                    rendered_str += chevron.render(
                        src_file, self.template_dict)
            return rendered_str == out_file.read()

    def _write_files(self):
        if self.out_path.exists():
            self.out_path.chmod(0o644)
        with open(self.out_path, 'w') as out_file:
            for src_path in self.src_paths:
                with open(src_path, 'r') as src_file:
                    rendered_str = chevron.render(
                        src_file, self.template_dict)
                out_file.write(rendered_str)
        self.out_path.chmod(0o544 if self.executable else 0o444)
