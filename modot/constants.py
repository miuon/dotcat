from pathlib import Path

HOST_CONFIG_FILE = Path('config.yaml')
MODULE_CONFIG_FILE = Path('module.yaml')
MODOT_DIR = Path('~/.local/share/modot').expanduser()
DEPLOYED_HOST = MODOT_DIR / HOST_CONFIG_FILE
ACTIVE_THEME_PATH = MODOT_DIR / Path('theme')
ACTIVE_COLOR_PATH = MODOT_DIR / Path('color.yaml')
