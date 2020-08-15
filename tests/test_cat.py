'''Test theme/color setting and templating.'''
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
import unittest
from unittest.mock import Mock

from modot.cat import Cat, ImproperOutpathError
from modot.rule import Rule
from modot.templater import FakeTemplater, Templater


class TestCat(unittest.TestCase):
    '''Test concat module configuration and magic methods.'''
    def setUp(self):
        '''Set up some tempfile objects and write to them.'''
        self.tmpdir_handle = TemporaryDirectory()
        self.tmpdir = Path(self.tmpdir_handle.name)
        srcfile1_handle = NamedTemporaryFile()
        self.srcfile1 = Path(srcfile1_handle.name)
        srcfile2_handle = NamedTemporaryFile()
        self.srcfile2 = Path(srcfile2_handle.name)
        outfile_handle = NamedTemporaryFile()
        self.outfile = Path(outfile_handle.name)
        self.handles = (srcfile1_handle, srcfile2_handle, outfile_handle)

    def tearDown(self):
        '''Ensure the tempfiles are destroyed.'''
        self.tmpdir_handle.cleanup()
        for handle in self.handles:
            handle.close()

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
            Rule(self.srcfile1, self.tmpdir / 'dne'),
            Rule(self.srcfile2, self.tmpdir / 'dne')]
        self.assertTrue(cat.check())

    def test_check_srcpath_not_file_fails(self):
        '''A cat where one src file isn't readable should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(self.tmpdir / 'srcdne', self.tmpdir / 'outdne'),
            Rule(self.srcfile2, self.tmpdir / 'outdne')]
        self.assertFalse(cat.check())

    def test_check_outpaths_dont_match_fails(self):
        '''A cat where the outpaths don't match should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(self.srcfile1, self.tmpdir / 'outdne'),
            Rule(self.srcfile2, self.tmpdir / 'differentdne')]
        self.assertFalse(cat.check())

    def test_check_outpath_isdir_fails(self):
        '''A cat where the outpath is currently a dir should fail checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(self.srcfile1, self.tmpdir),
            Rule(self.srcfile2, self.tmpdir)]
        self.assertFalse(cat.check())

    def test_check_final_single_rule_succeeds(self):
        '''A cat with one final rule should pass checks.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(self.srcfile1, self.tmpdir / 'outdne', final=True)]
        self.assertTrue(cat.check())

    def test_check_final_multiple_rules_fails(self):
        '''A cat with multiple rules should fail if any are final.'''
        cat = Cat(Mock(spec=Templater))
        cat.rules = [
            Rule(self.srcfile1, self.tmpdir / 'outdne', final=True),
            Rule(self.srcfile2, self.tmpdir)]
        self.assertFalse(cat.check())


class TestCatDeploy(unittest.TestCase):
    '''Test concat module deployment.'''

    def setUp(self):
        '''Set up some tempfile objects and write to them.'''
        self.tmpdir_handle = TemporaryDirectory()
        self.tmpdir = Path(self.tmpdir_handle.name)
        srcfile1_handle = NamedTemporaryFile()
        self.srcfile1 = Path(srcfile1_handle.name)
        srcfile2_handle = NamedTemporaryFile()
        self.srcfile2 = Path(srcfile2_handle.name)
        outfile_handle = NamedTemporaryFile()
        self.outfile = Path(outfile_handle.name)
        self.handles = (srcfile1_handle, srcfile2_handle, outfile_handle)

    def tearDown(self):
        '''Ensure the tempfiles are destroyed.'''
        self.tmpdir_handle.cleanup()
        for handle in self.handles:
            handle.close()

    def test_deploy_nonequal_files_write(self):
        '''A cat that would change the content of the file should write it.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [
            Rule(self.srcfile1, self.outfile),
            Rule(self.srcfile2, self.outfile)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.srcfile2.write_text('background: {{ colorbg }}')
        self.outfile.write_text('some old garbage')
        cat.deploy()
        self.assertEqual(
            self.outfile.read_text(),
            'theme: cooltheme\nforeground: white\nbackground: blue')

    def test_deploy_outfile_dne_write(self):
        '''A cat that would change the content of the file should write it.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [
            Rule(self.srcfile1, self.tmpdir/'newoutfile'),
            Rule(self.srcfile2, self.tmpdir/'newoutfile')]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.srcfile2.write_text('background: {{ colorbg }}')
        cat.deploy()
        self.assertEqual(
            (self.tmpdir/'newoutfile').read_text(),
            'theme: cooltheme\nforeground: white\nbackground: blue')

    def test_deploy_file_dne_raises(self):
        '''A cat should raise an error if a src file dne.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [
            Rule(self.srcfile1, self.outfile),
            Rule(self.tmpdir/'dne', self.outfile)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.outfile.write_text('some old garbage')
        with self.assertRaises(FileNotFoundError):
            cat.deploy()

    def test_deploy_file_empty_ignored(self):
        '''A cat should not add anything to the outfile for an empty src.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [
            Rule(self.srcfile1, self.outfile),
            Rule(self.srcfile2, self.outfile)]
        self.srcfile1.write_text('something cool\nnewline')
        self.srcfile2.write_text('')
        self.outfile.write_text('some old garbage')
        cat.deploy()
        self.assertEqual(
            self.outfile.read_text(),
            'something cool\nnewline')

    def test_deploy_equal_files_no_write(self):
        '''A cat that would not change the outfile shouldn't open it.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        outpathspy = Mock(wraps=self.outfile)
        cat.rules = [Rule(self.srcfile1, outpathspy)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.outfile.write_text('theme: cooltheme\nforeground: white')
        cat.deploy()
        # This is implementation-dependent -- look for a better option
        outpathspy.write_text.assert_not_called()

    def test_deploy_equal_files_flag_force_write(self):
        '''force_rewrite flag with equal output still writes the outfile.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        outpathspy = Mock(wraps=self.outfile)
        cat.rules = [
            Rule(self.srcfile1, outpathspy),
            Rule(self.srcfile2, outpathspy, force_rewrite=True)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.outfile.write_text('theme: cooltheme\nforeground: white')
        cat.deploy()
        # This is implementation-dependent -- look for a better option
        outpathspy.write_text.assert_called()

    def test_deploy_differing_outpaths_raises(self):
        '''If deploying rules with differing outpaths, raise an error.'''
        cat = Cat(FakeTemplater(
            self.tmpdir, {}))
        cat.rules = [
            Rule(self.srcfile1, self.outfile),
            Rule(self.srcfile2, self.tmpdir/'dne', force_rewrite=True)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.outfile.write_text('theme: cooltheme\nforeground: white')
        with self.assertRaises(ImproperOutpathError):
            cat.deploy()

    def test_deploy_permissions_readonly(self):
        '''The output file should have readonly permissions.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [Rule(self.srcfile1, self.outfile)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.outfile.write_text('theme: cooltheme\nforeground: white')
        self.outfile.chmod(0o000)
        cat.deploy()
        self.assertEqual(0o100444, self.outfile.stat().st_mode)

    def test_deploy_permissions_executable(self):
        '''The exec flag should cause the output file to be executable.'''
        cat = Cat(FakeTemplater(
            self.tmpdir,
            {'theme': 'cooltheme', 'colorfg': 'white', 'colorbg': 'blue'}))
        cat.rules = [
            Rule(self.srcfile1, self.outfile),
            Rule(self.srcfile2, self.outfile, executable=True)]
        self.srcfile1.write_text('theme: {{theme}}\nforeground: {{colorfg}}')
        self.srcfile2.write_text('')
        self.outfile.write_text('theme: cooltheme\nforeground: white')
        self.outfile.chmod(0o000)
        cat.deploy()
        self.assertEqual(0o100544, self.outfile.stat().st_mode)
