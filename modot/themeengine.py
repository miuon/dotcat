import asyncio
import chevron
import shutil
import sys
import yaml

from pathlib import Path
from typing import List

from .constants import *
from .utils import link_atomic

class ThemeEngine():
    def __init__(self, host_path: Path):
        if not host_path or not host_path.is_file():
            sys.exit('No deployed theme; run modot deploy <host_config>')
        with open(host_path, 'r') as stream:
            host_config = yaml.safe_load(stream)

        self.themes_path = Path(host_config['themes']).expanduser()
        self.colors_path = Path(host_config['colors']).expanduser()
        self.default_theme = host_config.get('default_theme', '')
        self.default_color = host_config.get('default_color', '')
        self.setup_actions = []
        self.cat_actions = {}

        self.read_modules(
                [Path(domain).expanduser() for domain in
                    host_config.get('domains', [])],
                host_config.get('modules', []))

    def read_modules(self, domains: List[str], modules: List[str]):
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
                        self.read_fileconf(filepath, fileconf)

    def read_fileconf(self, filepath: Path, fileconf: dict):
        out_str = fileconf.get('out', '')
        if not out_str: # TODO: try/catch?
            sys.exit(f'No output specified for {filepath}')
        out_path = Path(out_str).expanduser()
        if fileconf.get('dir_contents', False):
            if not filepath.is_dir():
                sys.exit(f'dir_contents used on non-dir: {filepath}')
            if out_path.exists() and not out_path.is_dir():
                sys.exit(f'{filepath} exists and is not a directory')
            self.setup_actions.append(MakeDirAction(out_path))
            for src_path in [p for p in filepath.iterdir() if p.is_file()]:
                out_file_path = out_path / src_path.name
                cat_action = self.cat_actions.get(str(out_file_path), None)
                if cat_action:
                    cat_action.add_path(src_path, fileconf)
                else:
                    self.cat_actions[str(out_file_path)] = CatAction(
                            src_path, out_file_path, fileconf)

        else:
            cat_action = self.cat_actions.get(str(out_path), None)
            if cat_action:
                cat_action.add_path(filepath, fileconf)
            else:
                self.setup_actions.append(MakeDirAction(out_path.parent))
                self.cat_actions[str(out_path)] = CatAction(
                        filepath, out_path, fileconf)

    def list_themes(self) -> List[str]:
        return [path.stem for path in self.themes_path.iterdir()]

    def list_colors(self):
        return [path.stem for path in self.colors_path.iterdir()]

    def set_theme(self, name):
        link_atomic(self.themes_path /
                Path(name).with_suffix('.yaml'), ACTIVE_THEME_PATH)
        if ACTIVE_COLOR_PATH.exists():
            self.read_template_dict()

    def set_color(self, name):
        link_atomic(self.colors_path /
                Path(name).with_suffix('.yaml'), ACTIVE_COLOR_PATH)
        if ACTIVE_THEME_PATH.exists():
            self.read_template_dict()

    def read_template_dict(self):
        if (not ACTIVE_COLOR_PATH.exists() or
                not ACTIVE_THEME_PATH.exists()):
            sys.exit(f'Failed to properly set color/theme')
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            color_dict = yaml.safe_load(stream)
        with open(ACTIVE_THEME_PATH, 'r') as stream:
            theme_dict = yaml.safe_load(stream)
        # TODO: deep merge
        self.template_dict = {**color_dict, **theme_dict}

    def print_actions(self):
        for action in self.setup_actions:
            print(action)
        for action in self.cat_actions.values():
            print(action)

    def deploy(self):
        for action in self.setup_actions:
            action.run()
        for action in self.cat_actions.values():
            action.run(self.template_dict)

class MakeDirAction():
    def __init__(self, path: Path):
        self.path = path

    def __repr__(self) -> str:
        return f'Create directory: {self.path}'

    def run(self):
        if self.path.is_symlink():
            self.path.unlink()
        elif self.path.exists() and not self.path.is_dir():
            sys.exit(f'Found a non-dir at {self.path} while trying to mkdir.')
        self.path.mkdir(parents=True, exist_ok=True)

class CatAction():
    def __init__(self, src_path: Path, out_path: Path, options: dict):
        self.src_paths = [src_path]
        self.out_path = out_path
        self.executable = options.get('exec', False)
        self.final = options.get('final', False)

    def __repr__(self) -> str:
        return f'Cat: {self.src_paths} -> {self.out_path}'

    def add_path(self, src_path: Path, options: dict):
        self.src_paths.append(src_path)
        self.executable = self.executable or options.get('exec', False)
        self.final = self.final or options.get('final', False)

    def run(self, template_dict: dict):
        self.template_dict = template_dict
        # TODO: perhaps add a check step for this stuff?
        if self.final and len(self.src_paths) > 1:
            sys.exit(f'Multiple rules writing to final path {self.out_path}')
        if self.out_path.is_dir():
            sys.exit(f'Target {self.out_path} is a directory, please delete')
        if self.out_path.is_symlink():
            self.out_path.unlink()
        if not self.files_equal(template_dict):
            self.write_files(template_dict)

    def files_equal(self) -> bool:
        if not self.out_path.is_file():
            return False
        with open(self.out_path, 'r') as out_file:
            rendered_str = ''
            for src_path in self.src_paths:
                with open(src_path, 'r') as src_file:
                    rendered_str += chevron.render(
                            src_file, self.template_dict)
            return rendered_str == out_file.read()

    def write_files(self, template_dict: dict):
        if self.out_path.exists():
            self.out_path.chmod(0o644)
        with open(self.out_path, 'w') as out_file:
            for src_path in self.src_paths:
                with open(src_path, 'r') as src_file:
                    rendered_str = chevron.render(
                            src_file, self.template_dict)
                out_file.write(rendered_str)
        self.out_path.chmod(0o544 if self.executable else 0o444)

