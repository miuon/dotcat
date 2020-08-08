'''Provides an object to handle templating themes/colors.'''
import os
from pathlib import Path
from typing import List, Optional

from modot.hostconfig import HostConfig


class Templater:
    '''Manages theme/color state and provides a function for templating.'''
    def __init__(
            self, modot_path: Path, host_config: Optional[HostConfig] = None):
        '''Initialize the templater and inject dependencies.'''
        self.modot_path = modot_path
        self.host_cfg = host_config

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
        raise NotImplementedError

    def set_color(self, name: str):
        '''Set the active color.'''
        raise NotImplementedError

    def template(self, src_string: str) -> str:
        '''Template the provided string with the active theme and color.'''
        raise NotImplementedError

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


class _ThemeColorCache:
    def __init__(self):
        raise NotImplementedError

    def invalidate(self):
        '''Invalidate the themecolor cache.'''
        raise NotImplementedError

    def get_themecolor(self) -> dict:
        '''Return the themecolor dict, either from files or cache.'''
        raise NotImplementedError


class LinkMalformedError(Exception):
    pass
