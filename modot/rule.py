'''Provides a value object to represent a concatenation rule.'''
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Rule:
    '''Represents a single concatenation rule and its flag options.'''
    src: Path
    out: Path
    executable: bool = False
    final: bool = False
    force_rewrite: bool = False
