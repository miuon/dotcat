import os

from pathlib import Path

from .constants import *

def get_deployed_host():
    if DEPLOYED_HOST.exists():
        if not DEPLOYED_HOST.is_symlink():
            sys.exit('Non-symlink deployed host, check ~/.local/share/modot')
        else:
            return DEPLOYED_HOST.resolve()
    else:
        return None

def link_atomic(file_path, link_path):
    tmp_path = link_path.parent / Path('modottmp')
    os.symlink(file_path, tmp_path)
    os.rename(tmp_path, link_path)
