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
        '''Return a string representation of this concat.'''
        raise NotImplementedError

    def __bool__(self) -> bool:
        '''Return true if this cat has any rules.'''
        return bool(self.rules)

    def check(self) -> bool:
        '''Check if this concatenation can be run successfully.'''
        src_paths = [rule.src for rule in self.rules]
        out_set = {rule.out for rule in self.rules}
        final = any(rule.final for rule in self.rules)
        if len(out_set) > 1:
            return False
        if final and len(self.rules) > 1:
            return False
        if self.rules[0].out.is_dir():
            return False
        for src_path in src_paths:
            if not src_path.is_file():
                return False
        return True

    def execute(self):
        '''Concatenate the configured source paths to write the target.'''
        raise NotImplementedError
