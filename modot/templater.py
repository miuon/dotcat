'''Provides an object to handle templating themes/colors.'''
import os
from pathlib import Path
from typing import List, Optional

import chevron
import yaml

from modot.hostconfig import HostConfig


class Templater:
    '''Manages theme/color state and provides a function for templating.'''
    def __init__(
            self, modot_path: Path, host_config: Optional[HostConfig] = None):
        '''Initialize the templater and inject dependencies.'''
        self.modot_path = modot_path
        self.host_cfg = host_config
        self._themecolor_cache: Optional[dict] = None

    def get_theme(self) -> Optional[str]:
        '''Return the currently deployed theme or None.'''
        return self._retrieve_config_link(self.modot_path/'theme.yaml')

    def get_color(self) -> Optional[str]:
        '''Return the currently deployed color or None.'''
        return self._retrieve_config_link(self.modot_path/'color.yaml')

    def list_themes(self) -> List[str]:
        '''Return all available themes.'''
        return self._get_directory_yaml_names(self.host_cfg.themes_path)

    def list_colors(self) -> List[str]:
        '''Return all available colors.'''
        return self._get_directory_yaml_names(self.host_cfg.colors_path)

    def set_theme(self, name: str):
        '''Set the active theme.'''
        new_theme_path = self.host_cfg.themes_path / (name + '.yaml')
        (self.modot_path/'theme.yaml').unlink(missing_ok=True)
        (self.modot_path/'theme.yaml').symlink_to(new_theme_path)
        self._themecolor_cache = None

    def set_color(self, name: str):
        '''Set the active color.'''
        new_color_path = self.host_cfg.colors_path / (name + '.yaml')
        (self.modot_path/'color.yaml').unlink(missing_ok=True)
        (self.modot_path/'color.yaml').symlink_to(new_color_path)
        self._themecolor_cache = None

    def template(self, src_string: str) -> str:
        '''Template the provided string with the active theme and color.'''
        if self._themecolor_cache is None:
            self._themecolor_cache = self._read_themecolor_config()
        return chevron.render(src_string, self._themecolor_cache)

    def _read_themecolor_config(self) -> dict:
        '''Read and merge the active theme and color configs.'''
        active_theme = self.modot_path/'theme.yaml'
        active_color = self.modot_path/'color.yaml'
        if (not active_theme.exists() or not active_color.exists()):
            raise LinkMalformedError
        with open(active_theme, 'r') as stream:
            theme_dict = yaml.safe_load(stream)
        with open(active_color, 'r') as stream:
            color_dict = yaml.safe_load(stream)
        return {**color_dict, **theme_dict}

    @staticmethod
    def _retrieve_config_link(active_path: Path):
        if not active_path.exists():
            return None
        if not active_path.is_symlink():
            raise LinkMalformedError
        link = Path(os.readlink(active_path))
        if link.suffix not in ('.yml', '.yaml'):
            raise LinkMalformedError
        return link.stem

    @staticmethod
    def _get_directory_yaml_names(dir_path: Path):
        if not dir_path.is_dir():
            raise FileNotFoundError
        return [cfg_path.stem for cfg_path in dir_path.iterdir()]


class FakeTemplater(Templater):
    '''Fake templater that takes a dict to use for templating.'''
    def __init__(self, modot_path: Path, template_dict: dict):
        '''Save the fake dict.'''
        super().__init__(self, modot_path)
        self.template_dict = template_dict

    def template(self, src_string: str) -> str:
        '''Template the string with the explicitly specified dictionary.'''
        return chevron.render(src_string, self.template_dict)


class LinkMalformedError(Exception):
    '''Raised when one of the symlinks is formatted incorrectly.'''
