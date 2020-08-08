'''Provides an object to handle templating themes/colors.'''
from pathlib import Path
from typing import List, Optional

from modot.hostconfig import HostConfig


class Templater:
    '''Manages theme/color state and provides a function for templating.'''
    def __init__(
            self, modot_path: Path, hostconfig: Optional[HostConfig] = None):
        '''Initialize the templater and inject dependencies.'''
        raise NotImplementedError

    def get_theme(self) -> Optional[str]:
        '''Return the currently deployed theme or None.'''
        raise NotImplementedError

    def get_color(self) -> Optional[str]:
        '''Return the currently deployed color or None.'''
        raise NotImplementedError

    def list_themes(self) -> List[str]:
        '''Return all available themes.'''
        raise NotImplementedError

    def list_colors(self) -> List[str]:
        '''Return all available colors.'''
        raise NotImplementedError

    def set_theme(self, name: str):
        '''Set the active theme.'''
        raise NotImplementedError

    def set_color(self, name: str):
        '''Set the active color.'''
        raise NotImplementedError

    def template(self, src_string: str) -> str:
        '''Template the provided string with the active theme and color.'''
        raise NotImplementedError


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
