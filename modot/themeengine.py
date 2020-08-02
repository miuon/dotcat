import asyncio
import chevron
import os
import shutil
import sys
import yaml

from pathlib import Path

from .constants import *
from .utils import link_atomic

class ThemeEngine():
    def __init__(self, host_path):
        if not host_path or not host_path.is_file():
            sys.exit('No deployed theme; run modot deploy <host_config>')
        with open(host_path, 'r') as stream:
            host_config = yaml.safe_load(stream)

        self.domains = [Path(domain).expanduser() for
                domain in host_config.get('domains', [])]
        self.themes_path = Path(host_config['themes']).expanduser()
        self.colors_path = Path(host_config['colors']).expanduser()
        self.default_theme = host_config.get('default_theme', '')
        self.default_color = host_config.get('default_color', '')
        self.modules = host_config.get('modules', [])
        self.file_tracker = {}
        self.setup_actions = []
        # TODO: will need more complex type to avoid noop modifications
        self.cat_actions = []

        self.read_modules()

    def read_modules(self):
        for domain in self.domains:
            domain_path = Path(domain).expanduser()
            for module_str in self.modules:
                module_path = domain_path / Path(module_str)
                module_conf_path = module_path / MODULE_CONFIG_FILE
                if module_conf_path.exists():
                    with open(module_conf_path, 'r') as stream:
                        module_config = yaml.safe_load(stream)
                    if module_config is None:
                        module_config = {}
                    for filestr, fileconf in module_config.items():
                        self.read_fileconf(module_path, filestr, fileconf)

    def read_fileconf(self, module_path, filestr, fileconf):
        paths = sorted(module_path.glob(filestr))
        readable_path = str(module_path / Path(filestr))
        out_str = fileconf.get('out', '')
        if not out_str: # TODO: try/catch?
            sys.exit(f'No output specified for {readable_path}')
        out_path = Path(out_str).expanduser()
        if len(paths) > 1:
            # dir out
            # grab all the relative paths somehow?
            # (maybe relative to module_path?)
            # (but that's not quite the right behavior -- rethink this)
            # could also define a seperate action for it
            # might be more correct vis a vis not reading file state early
            pass
        elif len(paths) == 1:
            path = paths[0]
            if self.file_tracker.get(str(out_path), False):
                self.cat_actions.append(CatAction(path, out_path))
            else:
                self.file_tracker[str(out_path)] = True
                self.setup_actions.append(MakeDirAction(out_path.parent))
                self.setup_actions.append(RemoveAction(out_path))
                self.cat_actions.append(CatAction(path, out_path))
        else:
            sys.exit(f'Could not resolve {readable_path}')

    def read_color_file(self):
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            self.color_dict = yaml.safe_load(stream)

    def list_themes(self):
        return [os.path.splitext(fn)[0] for fn in os.listdir(self.themes_path)]

    def list_colors(self):
        return [os.path.splitext(fn)[0] for fn in os.listdir(self.colors_path)]

    def set_theme(self, name):
        link_atomic(self.themes_path / Path(name + '.yaml'), ACTIVE_THEME_PATH)
        if ACTIVE_COLOR_PATH.exists():
            self.read_template_dict()

    def set_color(self, name):
        link_atomic(self.colors_path / Path(name + '.yaml'), ACTIVE_COLOR_PATH)
        if ACTIVE_THEME_PATH.exists():
            self.read_template_dict()

    def read_template_dict(self):
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            color_dict = yaml.safe_load(stream)
        with open(ACTIVE_THEME_PATH, 'r') as stream:
            theme_dict = yaml.safe_load(stream)
        # TODO: deep merge
        self.template_dict = {**color_dict, **theme_dict}

    def print_actions(self):
        for action in self.setup_actions:
            print(action)
        for action in self.cat_actions:
            print(action)

    def deploy(self):
        for action in self.setup_actions:
            action.run()
        for action in self.cat_actions:
            action.run(self.template_dict)

class MakeDirAction():
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'Create directory: {self.path}'

    def run(self):
        self.path.mkdir(parents=True, exist_ok=True)

class RemoveAction():
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'Remove: {self.path}'

    def run(self):
        self.path.unlink(missing_ok=True)

class CatAction():
    def __init__(self, src_path, out_path):
        self.src_path = src_path
        self.out_path = out_path

    def __repr__(self):
        return f'Cat: {self.src_path} -> {self.out_path}'

    def run(self, template_dict):
        if self.out_path.exists():
            self.out_path.chmod(0o644)
        with open(self.src_path, 'r') as src_file:
            rendered_str = chevron.render(src_file, template_dict)
        with open(self.out_path, 'a') as out_file:
            out_file.write(rendered_str)
        self.out_path.chmod(0o444)

