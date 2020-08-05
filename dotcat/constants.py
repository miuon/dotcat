'''Constants to define magic paths/filenames for dotcat.'''
from pathlib import Path

HOST_CONFIG_FILE = Path('config.yaml')
MODULE_CONFIG_FILE = Path('module.yaml')
DOTCAT_DIR = Path('~/.local/share/dotcat').expanduser()
DEPLOYED_HOST = DOTCAT_DIR / HOST_CONFIG_FILE
ACTIVE_THEME_PATH = DOTCAT_DIR / Path('theme.yaml')
ACTIVE_COLOR_PATH = DOTCAT_DIR / Path('color.yaml')
