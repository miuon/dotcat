'''Provides an object to handle templating themes/colors.'''
from pathlib import Path
from typing import List, Optional

from modot.hostconfig import HostConfig


class Templater():
    '''Manages theme/color state and provides a function for templating.'''
    def __init__(self, modot_path: Path, hostconfig: Optional(HostConfig)):
        '''Initialize the templater and inject dependencies.'''

    def get_theme(self) -> Optional[str]:
        '''Return the currently deployed theme or None.'''

    def get_color(self) -> Optional[str]:
        '''Return the currently deployed color or None.'''

    def list_themes(self) -> List[str]:
        '''Return all available themes.'''

    def list_colors(self) -> List[str]:
        '''Return all available colors.'''

    def set_theme(self, name: str):
        '''Set the active theme.'''

    def set_color(self, name: str):
        '''Set the active color.'''

    def template(self, src_string: str) -> str:
        '''Template the provided string with the active theme and color.'''


class _ThemeColorCache():
    def __init__(self):
        pass

    def invalidate(self):
        '''Invalidate the themecolor cache.'''

    def get_themecolor(self) -> dict:
        '''Return the themecolor dict, either from files or cache.'''
