'''Test utility functions used for module location/parsing.'''
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from modot.hostconfig import HostConfig
from modot import module_utils
from modot.module_utils import (get_module_paths, get_rules,
                                DuplicateDomainError)
from modot.rule import Rule


def _expanduserstub(path: Path) -> Path:
    '''Crude stub for expanduser that does a simple string replacement.'''
    return Path(str(path).replace('~', '/fakehome'))


class TestModuleUtils(unittest.TestCase):
    '''Test the module utilities.'''
    def setUp(self):
        '''Set up a root temp directory and get its path for convenience.'''
        self.root_handle = TemporaryDirectory()
        self.root = Path(self.root_handle.name)
        module_utils.Path.expanduser = _expanduserstub

    def tearDown(self):
        self.root_handle.cleanup()

    def test_get_module_paths_correct_order(self):
        '''Should return module paths in order, skipping if dne.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'dom1', self.root/'dom2']
        host_cfg.modules = ['mod1', 'mod2']
        (self.root/'dom1').mkdir()
        (self.root/'dom2').mkdir()
        (self.root/'dom1'/'mod1').mkdir()
        (self.root/'dom1'/'mod2').mkdir()
        (self.root/'dom2'/'mod2').mkdir()
        mod_gen = get_module_paths(host_cfg)
        self.assertEqual(
            [next(mod_gen), next(mod_gen), next(mod_gen)],
            [self.root/'dom1'/'mod1', self.root/'dom1'/'mod2',
             self.root/'dom2'/'mod2'])
        with self.assertRaises(StopIteration):
            next(mod_gen)

    def test_get_module_paths_domain_dne_throws(self):
        '''Should error when a domain path does not exist.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'dne']
        host_cfg.modules = ['mod']
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(FileNotFoundError):
            next(mod_gen)

    def test_get_module_paths_domain_is_file_throws(self):
        '''Should error when a domain path points to a file.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'is_file']
        host_cfg.modules = ['mod']
        (self.root/'is_file').touch()
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(NotADirectoryError):
            next(mod_gen)

    def test_get_module_paths_duplicate_domain_throws(self):
        '''Should error when a domain path is duplicated.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'seeingdouble', self.root/'seeingdouble']
        host_cfg.modules = ['mod']
        (self.root/'seeingdouble').mkdir()
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(DuplicateDomainError):
            next(mod_gen)

    def test_get_module_paths_module_dne_ignore(self):
        '''Should ignore a module path that does not exist.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'dom1']
        host_cfg.modules = ['mod']
        (self.root/'dom1').mkdir()
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(StopIteration):
            next(mod_gen)

    def test_get_module_paths_module_is_file_throws(self):
        '''Should error when a module path points to a file.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.root/'dom1']
        host_cfg.modules = ['mod']
        (self.root/'dom1').mkdir()
        (self.root/'dom1'/'mod').touch()
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(NotADirectoryError):
            next(mod_gen)

    def test_get_rules(self):
        '''Should return basic rules from the module config.'''
        module_path = self.root / 'mod1'
        module_cfg_path = self.root / 'mod1' / 'module.yaml'
        module_path.mkdir()
        module_cfg_path.write_text('infile1.txt:\n'
                                   '  out: ~/outfile\n'
                                   'infile2.txt:\n'
                                   '  out: ~/outfile2')
        rules = get_rules(module_path)
        self.assertEqual(rules, [
            Rule(module_path/'infile1.txt', Path('/fakehome/outfile')),
            Rule(module_path/'infile2.txt', Path('/fakehome/outfile2'))])

    def test_get_rules_path_dne_raises(self):
        '''Should raise filenotfound if the module path DNE.'''
        module_path = self.root / 'mod1'
        with self.assertRaises(FileNotFoundError):
            get_rules(module_path)

    def test_get_rules_path_not_dir_throws(self):
        '''Should raise filenotfound if the module file is not a dir.'''
        module_path = self.root / 'mod1'
        module_path.touch()
        with self.assertRaises(NotADirectoryError):
            get_rules(module_path)

    def test_get_rules_no_module_file_throws(self):
        '''Should raise filenotfound if the module config DNE.'''
        module_path = self.root / 'mod1'
        module_path.mkdir()
        with self.assertRaises(FileNotFoundError):
            get_rules(module_path)

    def test_get_rules_with_flags(self):
        '''Should return a rule with all normal flags set from a config.'''
        module_path = self.root / 'mod1'
        module_cfg_path = self.root / 'mod1' / 'module.yaml'
        module_path.mkdir()
        module_cfg_path.write_text('infile1.txt:\n'
                                   '  out: ~/outfile\n'
                                   '  final: true\n'
                                   '  exec: true\n'
                                   '  force_rewrite: true')
        rules = get_rules(module_path)
        self.assertEqual(rules, [
            Rule(module_path/'infile1.txt', Path('/fakehome/outfile'),
                 final=True, executable=True, force_rewrite=True)])

    def test_get_rules_dir_contents(self):
        '''dir_contents flag should produce rules for all files in a subdir.'''
        module_path = self.root / 'mod1'
        module_cfg_path = self.root / 'mod1' / 'module.yaml'
        module_subdir_path = self.root / 'mod1' / 'subdir'
        module_path.mkdir()
        module_subdir_path.mkdir()
        (module_subdir_path/'file1.txt').touch()
        (module_subdir_path/'file2.txt').touch()
        module_cfg_path.write_text('subdir:\n'
                                   '  out: ~/outdir\n'
                                   '  dir_contents: true')
        rules = get_rules(module_path)
        self.assertCountEqual(rules, [
            Rule(module_path/'subdir'/'file1.txt',
                 Path('/fakehome/outdir/file1.txt')),
            Rule(module_path/'subdir'/'file2.txt',
                 Path('/fakehome/outdir/file2.txt'))])

    def test_get_rules_dir_contents_dir_dne_throws(self):
        '''Parsing a dir_contents rule for a dir that dne should fail.'''
        module_path = self.root / 'mod1'
        module_cfg_path = self.root / 'mod1' / 'module.yaml'
        module_path.mkdir()
        module_cfg_path.write_text('subdir_dne:\n'
                                   '  out: /outdir\n'
                                   '  dir_contents: true')
        with self.assertRaises(FileNotFoundError):
            get_rules(module_path)

    def test_get_rules_dir_contents_not_dir_throws(self):
        '''Parsing a dir_contents rule for a non-dir should fail.'''
        module_path = self.root / 'mod1'
        module_cfg_path = self.root / 'mod1' / 'module.yaml'
        module_path.mkdir()
        module_subdir_path = self.root / 'mod1' / 'subdir_file'
        module_subdir_path.touch()
        module_cfg_path.write_text('subdir_file:\n'
                                   '  out: ~/outdir\n'
                                   '  dir_contents: true')
        with self.assertRaises(NotADirectoryError):
            get_rules(module_path)
