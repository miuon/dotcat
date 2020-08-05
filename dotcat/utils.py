'''Miscellaneous utilities.'''
import os
import sys
from pathlib import Path
from typing import Optional

from dotcat.constants import DEPLOYED_HOST


def get_deployed_host() -> Optional[Path]:
    '''Returns the path to the deployed host, if there is one.'''
    if DEPLOYED_HOST.exists():
        if not DEPLOYED_HOST.is_symlink():
            sys.exit('Non-symlink deployed host, check ~/.local/share/dotcat')
        else:
            return DEPLOYED_HOST.resolve()
    else:
        return None


def link_atomic(file_path: Path, link_path: Path):
    '''Creates a symlink, replacing preexisting files atomically.'''
    tmp_path = link_path.parent / Path('dotcattmp')
    os.symlink(file_path, tmp_path)
    os.rename(tmp_path, link_path)
