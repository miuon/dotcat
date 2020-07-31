import asyncio
import chevron
import os
import shutil
import sys
import yaml

from pathlib import Path

from .constants import *
from .utils import get_deployed_host, link_atomic

class ThemeEngine():
    def __init__(self):
        self.directories = []
        self.links = []
        self.color_dict = {}
        self.templates = []
        self.concats = []
        self.reload_actions = []
        self.restart_actions = []

    @classmethod
    def host_only(cls, host_path):
        if not host_path or not host_path.is_file():
            sys.exit('No deployed theme; run modot deploy <host_config>')
        config = cls()
        config.read_host(host_path)
        return config

    def read_config(self, host_path):
        self.read_host(host_path)
        self.read_modules()

    def read_host(self, host_path):
        with open(host_path, 'r') as stream:
            host_config = yaml.safe_load(stream)
        self.common_path = Path(host_config['common_path']).expanduser()
        self.host_path = Path(host_config['host_path']).expanduser()
        self.themes_path = Path(host_config['themes_path']).expanduser()
        self.colors_path = Path(host_config['colors_path']).expanduser()
        self.default_theme = host_config.get('default_theme', '')
        self.default_color = host_config.get('default_color', '')
        self.modules = host_config['modules']

    def read_modules(self):
        self.read_color_file()
        for module_name in self.modules:
            module_conf_path = self.common_path / Path(module_name) / Path(
                    'module.yaml')
            self.read_module(module_conf_path, module_name)

    def read_module(self, module_conf_path, module_name):
        with open(module_conf_path, 'r') as stream:
            module_config = yaml.safe_load(stream)
        if module_config is None:
            module_config = {}
        self.read_directories(module_config.get('directories', []))
        self.read_links(module_name, module_config.get('links', []))
        self.read_concats(module_config.get('concats', []))
        if module_config.get('reload'):
            self.reload_actions.append(Action(module_config.get('reload')))
        if module_config.get('restart'):
            self.restart_actions.append(Action(module_config.get('restart')))

    def read_directories(self, directories):
        for directory_str in directories:
            self.directories.append(Directory(Path(directory_str).expanduser()))

    def read_links(self, module_name, links):
        for link in links:
            link_from = link.get('from', '')
            if link.get('template'):
                self.templates.append(Template(
                        self.get_dir_path(link_from) /
                        Path(module_name) / Path(link['src']),
                        self.color_dict,
                        Path(link['tgt']).expanduser()))
            else:
                self.links.append(Link(
                        self.get_dir_path(link_from) /
                        Path(module_name) / Path(link['src']),
                        Path(link['tgt']).expanduser()))

    def read_concats(self, concats):
        for concat in concats:
            self.concats.append(Concat(
                [Path(src_path).expanduser() for src_path in concat['src']],
                Path(concat['out']).expanduser()))

    def get_dir_path(self, link_from):
        if not link_from or link_from in ('common', ''):
            return self.common_path
        if link_from in ('host'):
            return self.host_path
        if link_from in ('theme'):
            return ACTIVE_THEME_PATH
        sys.exit('Problem with "from" in module file') # TODO: helpful info

    def read_color_file(self):
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            self.color_dict = yaml.safe_load(stream)

    def list_themes(self):
        return os.listdir(self.themes_path)

    def list_colors(self):
        return [os.path.splitext(fn)[0] for fn in os.listdir(self.colors_path)]

    def set_theme(self, name):
        link_atomic(self.themes_path / Path(name), ACTIVE_THEME_PATH)

    def set_color(self, name):
        link_atomic(self.colors_path / Path(name + '.yaml'), ACTIVE_COLOR_PATH)

    def print_actions(self):
        print('=== Directories ===')
        for directory in self.directories:
            print(directory)
        print('=== Links ===')
        for link in self.links:
            print(link)
        print('=== Templates ===')
        for template in self.templates:
            print(template)
        print('=== Concats ===')
        for concat in self.concats:
            print(concat)
        print('=== Reloads ===')
        for action in self.reload_actions:
            print(action)
        print('=== Restarts ===')
        for action in self.restart_actions:
            print(action)

    def make_directories(self):
        for directory in self.directories:
            directory.make()

    def make_links(self):
        for link in self.links:
            link.make()

    def regenerate(self):
        for template in self.templates:
            template.make()
        for concat in self.concats:
            concat.make()

    def execute_reload(self):
        for action in self.reload_actions:
            asyncio.run(action.execute())

    def execute_restart(self):
        for action in self.restart_actions:
            asyncio.run(action.execute())

class Directory():
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'Directory: {self.path}'

    def make(self):
        self.path.mkdir(parents=True, exist_ok=True)

class Link():
    def __init__(self, file_path, link_path):
        self.file_path = file_path
        self.link_path = link_path

    def __repr__(self):
        return f'Link: {self.file_path} -> {self.link_path}'

    def check(self):
        return False # TODO

    def make(self):
        tmp_path = Path(self.link_path.parent) / Path('modottmp')
        os.symlink(self.file_path, tmp_path)
        os.rename(tmp_path, self.link_path)

class Template():
    def __init__(self, src_path, color_dict, tgt_path):
        self.src_path = src_path
        self.color_dict = color_dict
        self.tgt_path = tgt_path

    def __repr__(self):
        return f'Template: {self.src_path} -> {self.tgt_path}'

    def check(self):
        return False # TODO

    def make(self):
        # TODO
        with open(self.src_path, 'r') as src_file:
            rendered_str = chevron.render(src_file, self.color_dict)
        with open(self.tgt_path, 'w') as tgt_file:
            tgt_file.write(rendered_str)

class Concat():
    def __init__(self, src_list, out_path):
        self.src_list = src_list
        self.out_path = out_path

    def __repr__(self):
        list_str = ', '.join(str(src) for src in self.src_list)
        return f'Concat: {list_str} -> {str(self.out_path)}'

    def check(self):
        return False # TODO

    def make(self):
        with open(self.out_path, 'wb') as outfile:
            for src_path in self.src_list:
                with open(src_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)

class Action():
    def __init__(self, cmd):
        self.cmd = cmd

    def __repr__(self):
        return f'Execute: {self.cmd}'

    async def execute(self):
        modot_env = dict(os.environ)
        proc = await asyncio.create_subprocess_shell(
                self.cmd,
                env=modot_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        print(f'[{self.cmd!r} exited with {proc.returncode}]')
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
