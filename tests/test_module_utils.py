'''Test utility functions used for module location/parsing.'''
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from modot.hostconfig import HostConfig
from modot.module_utils import (get_module_paths, get_rules,
                                DuplicateDomainError)


class TestModuleUtils(unittest.TestCase):
    '''Test the module utilities.'''
    def setUp(self):
        '''Set up a root temp directory and get its path for convenience.'''
        self.root_handle = TemporaryDirectory()
        self.root = Path(self.root_handle.name)
        # TODO: consider moving these inline
        self.dom1 = self.root/'dom1'
        self.dom2 = self.root/'dom2'
        self.dom1.mkdir()
        self.dom2.mkdir()

    def tearDown(self):
        self.root_handle.cleanup()

    def test_get_module_paths_correct_order(self):
        '''Should return module paths in order, skipping if dne.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.dom1, self.dom2]
        host_cfg.modules = ['mod1', 'mod2']
        (self.dom1/'mod1').mkdir()
        (self.dom1/'mod2').mkdir()
        (self.dom2/'mod2').mkdir()
        mod_gen = get_module_paths(host_cfg)
        self.assertEqual(
                [next(mod_gen), next(mod_gen), next(mod_gen)],
                [self.dom1/'mod1', self.dom1/'mod2', self.dom2/'mod2'])
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
        host_cfg.domains = [self.dom1]
        host_cfg.modules = ['mod']
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(StopIteration):
            next(mod_gen)

    def test_get_module_paths_module_is_file_throws(self):
        '''Should error when a module path points to a file.'''
        host_cfg = HostConfig(None, None)
        host_cfg.domains = [self.dom1]
        host_cfg.modules = ['mod']
        (self.dom1/'mod').touch()
        mod_gen = get_module_paths(host_cfg)
        with self.assertRaises(NotADirectoryError):
            next(mod_gen)

    def test_get_rules(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_path_dne_throws(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_path_not_dir_throws(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_no_module_file_throws(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_dir_contents(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_dir_contents_dne_throws(self):
        ''''''
        raise unittest.SkipTest

    def test_get_rules_dir_contents_not_dir_throws(self):
        ''''''
        raise unittest.SkipTest
