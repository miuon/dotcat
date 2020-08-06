'''Manages stateful elements modot saves as symlinks.'''
import os
from pathlib import Path
import sys
from typing import List, Optional
import yaml

HOST_CONFIG_FILE = Path('config.yaml')
MODOT_DIR = Path('~/.local/share/modot').expanduser()
DEPLOYED_HOST = MODOT_DIR / HOST_CONFIG_FILE
ACTIVE_THEME_PATH = MODOT_DIR / Path('theme.yaml')
ACTIVE_COLOR_PATH = MODOT_DIR / Path('color.yaml')


class State():
    def __init__(self):
        MODOT_DIR.mkdir(parents=True, exist_ok=True)
        self.themecolor_dict = {}

    def set_host_path(self, host_path: Path):
        '''Set a symlink to preserve the deployed host file.'''
        deployed_host_tgt = self.get_deployed_host()
        if deployed_host_tgt:
            if deployed_host_tgt == host_path:
                print(f'Redeploying same host: {str(deployed_host_tgt)}')
            else:
                print(f'Deploying over old host: {str(deployed_host_tgt)}')
        else:
            print('Deploying host config: ' + str(host_path))
        self.link_atomic(host_path, DEPLOYED_HOST)

    @staticmethod
    def get_deployed_host() -> Optional[Path]:
        '''Returns the path to the deployed host, if there is one.'''
        if DEPLOYED_HOST.exists():
            if not DEPLOYED_HOST.is_symlink():
                sys.exit(
                    'Non-symlink deployed host, check ~/.local/share/modot')
            else:
                return DEPLOYED_HOST.resolve()
        else:
            return None

    def get_host_config(self) -> dict:
        # TODO: cacheing
        host_path = self.get_deployed_host()
        if not host_path or not host_path.is_file():
            sys.exit('No deployed host; run modot deploy <host_config>')
        with open(host_path, 'r') as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def get_theme():
        '''Return the currently deployed theme if it exists.'''
        if ACTIVE_THEME_PATH.exists():
            return Path(os.readlink(ACTIVE_THEME_PATH)).stem
        else:
            return None

    @staticmethod
    def get_color() -> Optional[str]:
        '''Return the currently deployed color if it exists.'''
        if ACTIVE_COLOR_PATH.exists():
            return Path(os.readlink(ACTIVE_COLOR_PATH)).stem
        else:
            return None

    def set_theme(self, name):
        '''Change the deployed theme file by changing the active theme link.'''
        self.link_atomic(Path(self.get_host_config()['themes']).expanduser() /
                         Path(name).with_suffix('.yaml'), ACTIVE_THEME_PATH)
        if ACTIVE_COLOR_PATH.exists():
            self._build_themecolor_dict()

    def set_color(self, name):
        '''Change the deployed color file by changing the active color link.'''
        self.link_atomic(Path(self.get_host_config()['colors']).expanduser() /
                         Path(name).with_suffix('.yaml'), ACTIVE_COLOR_PATH)
        if ACTIVE_THEME_PATH.exists():
            self._build_themecolor_dict()

    def list_themes(self) -> List[str]:
        themes_path = Path(self.get_host_config()['themes']).expanduser()
        return [path.stem for path in themes_path.iterdir()]

    def list_colors(self) -> List[str]:
        colors_path = Path(self.get_host_config()['colors']).expanduser()
        return [path.stem for path in colors_path.iterdir()]

    def get_themecolor_dict(self) -> dict:
        '''Read the template variables from the theme and color files.'''
        return self.themecolor_dict or self._build_themecolor_dict()

    def _build_themecolor_dict(self) -> dict:
        if (not ACTIVE_COLOR_PATH.is_symlink() or
                not ACTIVE_THEME_PATH.is_symlink()):
            sys.exit('Failed to properly set color/theme')
        with open(ACTIVE_COLOR_PATH, 'r') as stream:
            color_dict = yaml.safe_load(stream)
        with open(ACTIVE_THEME_PATH, 'r') as stream:
            theme_dict = yaml.safe_load(stream)
        self.themecolor_dict = {**color_dict, **theme_dict}
        return self.themecolor_dict

    @staticmethod
    def link_atomic(file_path: Path, link_path: Path):
        '''Creates a symlink, replacing preexisting files atomically.'''
        tmp_path = link_path.parent / Path('modottmp')
        os.symlink(file_path, tmp_path)
        os.rename(tmp_path, link_path)
