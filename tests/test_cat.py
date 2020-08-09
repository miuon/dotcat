'''Test theme/color setting and templating.'''
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
import unittest
from unittest.mock import Mock

from modot.cat import Cat
from modot.rule import Rule
from modot.templater import Templater


class TestCat(unittest.TestCase):
    '''Test templater configuration and usage.'''
    def setUp(self):
        '''Set up some tempfile objects and write to them.'''
        self.tmpdir = TemporaryDirectory()
        self.srcfile1 = NamedTemporaryFile()
        self.srcfile2 = NamedTemporaryFile()
        self.outfile = NamedTemporaryFile()

    def tearDown(self):
        '''Ensure the tempfiles are destroyed.'''
        self.tmpdir.cleanup()
        self.srcfile1.close()
        self.srcfile2.close()
        self.outfile.close()

    def test_bool_empty_isfalse(self):
        '''An empty cat object should return false.'''
        cat = Cat(Mock(spec=Templater))
        self.assertFalse(cat)

    def test_bool_nonempty_istrue(self):
        '''A cat object with a rule added should return false.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [Rule(Path(), Path())]
        self.assertTrue(cat)

    def test_str_empty_exists(self):
        '''An empty cat object should have a string representation.'''
        cat = Cat(Mock(spec=Templater))
        self.assertTrue(str(cat))

    def test_str_nonempty_exists(self):
        '''A non-empty cat object should have a string representation.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [Rule(Path(), Path())]
        self.assertTrue(str(cat))

    def test_check_srcpaths_exist_outpath_dne_succeeds(self):
        '''A cat with readable srcs and nonexistent out should pass checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.srcfile1.name),
                 Path(self.tmpdir.name) / Path('dne')),
            Rule(Path(self.srcfile2.name),
                 Path(self.tmpdir.name) / Path('dne'))]
        self.assertTrue(cat.check())

    def test_check_srcpath_not_file_fails(self):
        '''A cat where one src file isn't readable should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.tmpdir.name) / Path('srcdne'),
                 Path(self.tmpdir.name) / Path('outdne')),
            Rule(Path(self.srcfile2.name),
                 Path(self.tmpdir.name) / Path('outdne'))]
        self.assertFalse(cat.check())

    def test_check_outpaths_dont_match_fails(self):
        '''A cat where the outpaths don't match should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.srcfile1.name),
                 Path(self.tmpdir.name) / Path('outdne')),
            Rule(Path(self.srcfile2.name),
                 Path(self.tmpdir.name) / Path('differentdne'))]
        self.assertFalse(cat.check())

    def test_check_outpath_isdir_fails(self):
        '''A cat where the outpath is currently a dir should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.srcfile1.name), Path(self.tmpdir.name)),
            Rule(Path(self.srcfile2.name), Path(self.tmpdir.name))]
        self.assertFalse(cat.check())

    def test_check_final_single_rule_succeeds(self):
        '''A cat with one final rule should pass checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.srcfile1.name),
                 Path(self.tmpdir.name) / Path('outdne'),
                 final=True)]
        self.assertTrue(cat.check())

    def test_check_final_multiple_rules_fails(self):
        '''A cat with multiple rules should fail if any are final.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(Path(self.srcfile1.name),
                 Path(self.tmpdir.name) / Path('outdne'),
                 final=True),
            Rule(Path(self.srcfile2.name), Path(self.tmpdir.name))]
        self.assertFalse(cat.check())

    def test_execute_nonequal_files_write(self):
        '''A cat that would change the content of the file should write it.'''
        raise unittest.SkipTest

    def test_execute_equal_files_no_write(self):
        '''A cat that would not change the outfile shouldn't open it.'''
        raise unittest.SkipTest

    def test_execute_equal_files_flag_force_write(self):
        '''force_rewrite flag with equal output still writes the outfile.'''
        raise unittest.SkipTest
