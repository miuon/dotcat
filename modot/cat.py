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

    def __str__(self) -> str:
        '''Return a string representation of this concat.'''
        flag_strs = []
        if any(rule.final for rule in self.rules):
            flag_strs.append('final')
        if any(rule.executable for rule in self.rules):
            flag_strs.append('executable')
        if any(rule.force_rewrite for rule in self.rules):
            flag_strs.append('force_rewrite')
        flag_str = ', '.join(flag_strs)
        out = self.rules[0].out if self.rules else 'EMPTY'
        src_str = '\n'.join(f'    {rule.src}' for rule in self.rules)
        return f"Cat [{flag_str}]: {out}\n{src_str}"

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

    def deploy(self):
        '''Concatenate the configured source paths to write the target.'''
        raise NotImplementedError
