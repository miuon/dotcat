'''An object representing a single concatenation operation.'''
from typing import List

from modot.rule import Rule
from modot.templater import Templater


class Cat():
    '''Represents a concatenation operation.'''
    rules: List[Rule]

    def __init__(self, templater: Templater):
        '''Create an empty concatenation.'''
        self.rules = []
        self.templater = templater

    def __repr__(self) -> str:
        '''Print a representation of this concat.'''
        raise NotImplementedError

    def __bool__(self) -> bool:
        '''Return true if this cat has any rules.'''
        raise NotImplementedError

    def check(self) -> bool:
        '''Check if this concatenation can be run successfully.'''
        raise NotImplementedError

    def execute(self):
        '''Concatenate the configured source paths to write the target.'''
        raise NotImplementedError
