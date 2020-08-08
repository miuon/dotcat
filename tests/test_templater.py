'''Test theme/color setting and templating.'''
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from modot.hostconfig import HostConfig
from modot.templater import LinkMalformedError, Templater, _ThemeColorCache


class TestTemplater(unittest.TestCase):
    '''Test templater configuration and usage.'''

    def setUp(self):
        '''Set up some temp directories for test.'''
        self.link_dir = TemporaryDirectory()
        self.theme_dir = TemporaryDirectory()
        self.color_dir = TemporaryDirectory()

    def tearDown(self):
        self.link_dir.cleanup()
        self.theme_dir.cleanup()
        self.color_dir.cleanup()

    def test_get_theme(self):
        '''Test getting theme with a correctly formatted link.'''
        link_path = Path(self.link_dir.name)
        theme_link_path = Path(self.link_dir.name) / Path('theme.yaml')
        theme_tgt_path = Path(self.theme_dir.name) / Path('cooltheme.yaml')
        theme_tgt_path.touch()
        theme_link_path.symlink_to(theme_tgt_path)
        templater = Templater(link_path)
        self.assertEqual(templater.get_theme(), 'cooltheme')

    def test_get_theme_no_link_returns_none(self):
        '''Test getting theme with no link present.'''
        link_path = Path(self.link_dir.name)
        templater = Templater(link_path)
        self.assertIsNone(templater.get_theme())

    def test_get_theme_not_a_link_raises(self):
        '''Test getting theme when the active path isn't a link.'''
        link_path = Path(self.link_dir.name)
        theme_link_path = Path(self.link_dir.name) / Path('theme.yaml')
        theme_link_path.touch()
        templater = Templater(link_path)
        with self.assertRaises(LinkMalformedError):
            templater.get_theme()

    def test_get_theme_link_tgt_malformed_raises(self):
        '''Test getting theme from a malformed link target name.'''
        link_path = Path(self.link_dir.name)
        theme_link_path = Path(self.link_dir.name) / Path('theme.yaml')
        theme_tgt_path = Path(self.theme_dir.name) / Path('notyaml.txt')
        theme_tgt_path.touch()
        theme_link_path.symlink_to(theme_tgt_path)
        templater = Templater(link_path)
        with self.assertRaises(LinkMalformedError):
            templater.get_theme()

    def test_get_color(self):
        '''Test getting color with a correctly formatted link.'''
        link_path = Path(self.link_dir.name)
        color_link_path = Path(self.link_dir.name) / Path('color.yaml')
        color_tgt_path = Path(self.color_dir.name) / Path('coolcolor.yaml')
        color_tgt_path.touch()
        color_link_path.symlink_to(color_tgt_path)
        templater = Templater(link_path)
        self.assertEqual(templater.get_color(), 'coolcolor')

    def test_get_color_no_link_returns_none(self):
        '''Test getting color with no link present.'''
        link_path = Path(self.link_dir.name)
        templater = Templater(link_path)
        self.assertIsNone(templater.get_color())

    def test_get_color_not_a_link_raises(self):
        '''Test getting color when the active path isn't a link.'''
        link_path = Path(self.link_dir.name)
        color_path = Path(self.link_dir.name) / Path('color.yaml')
        color_path.touch()
        templater = Templater(link_path)
        with self.assertRaises(LinkMalformedError):
            templater.get_color()

    def test_get_color_link_malformed_raises(self):
        '''Test getting color from a malformed link target name.'''
        link_path = Path(self.link_dir.name)
        color_link_path = Path(self.link_dir.name) / Path('color.yaml')
        color_tgt_path = Path(self.color_dir.name) / Path('notyaml.txt')
        color_tgt_path.touch()
        color_link_path.symlink_to(color_tgt_path)
        templater = Templater(link_path)
        with self.assertRaises(LinkMalformedError):
            templater.get_color()

    def test_list_themes(self):
        '''Test listing the available themes.'''
        themes_path = Path(self.theme_dir.name)
        (themes_path / Path('cooltheme.yaml')).touch()
        (themes_path / Path('radtheme.yaml')).touch()
        host_config = HostConfig(themes_path, None)
        templater = Templater(Path(self.link_dir.name), host_config)
        self.assertCountEqual(
                templater.list_themes(), ['cooltheme', 'radtheme'])

    def test_list_themes_dir_empty(self):
        '''Test listing the themes with none available.'''
        themes_path = Path(self.theme_dir.name)
        host_config = HostConfig(themes_path, None)
        templater = Templater(Path(self.link_dir.name), host_config)
        self.assertCountEqual(templater.list_themes(), [])

    def test_list_themes_path_nonexistent_raises(self):
        '''Test listing the available themes when the dir does not exist.'''
        themes_path = Path(self.theme_dir.name) / Path('dne')
        host_config = HostConfig(themes_path, None)
        templater = Templater(Path(self.link_dir.name), host_config)
        with self.assertRaises(FileNotFoundError):
            templater.list_themes()

    def test_list_colors(self):
        '''Test listing the available colors.'''
        colors_path = Path(self.color_dir.name)
        (colors_path / Path('coolcolor.yaml')).touch()
        (colors_path / Path('radcolor.yaml')).touch()
        host_config = HostConfig(None, colors_path)
        templater = Templater(Path(self.link_dir.name), host_config)
        self.assertCountEqual(
                templater.list_colors(), ['coolcolor', 'radcolor'])

    def test_list_colors_dir_empty(self):
        '''Test listing the colors with none available.'''
        colors_path = Path(self.color_dir.name)
        host_config = HostConfig(None, colors_path)
        templater = Templater(Path(self.link_dir.name), host_config)
        self.assertCountEqual(templater.list_colors(), [])

    def test_list_color_path_nonexistent_raises(self):
        '''Test listing the available colors when the dir does not exist.'''
        colors_path = Path(self.color_dir.name) / Path('dne')
        host_config = HostConfig(None, colors_path)
        templater = Templater(Path(self.link_dir.name), host_config)
        with self.assertRaises(FileNotFoundError):
            templater.list_colors()

    def test_set_theme(self):
        '''Test setting the active theme.'''
        host_config = HostConfig(
                Path(self.theme_dir.name), Path(self.color_dir.name))
        templater = Templater(Path(self.link_dir.name), host_config)
        templater.set_theme('cooltheme')
        active_theme_path = Path(self.link_dir.name) / 'theme.yaml'
        self.assertEqual(  # this is maybe questionable
                os.readlink(active_theme_path),
                Path(self.theme_dir.name) / 'cooltheme.yaml')

    def test_set_color(self):
        '''Test setting the active color.'''
        host_config = HostConfig(
                Path(self.color_dir.name), Path(self.color_dir.name))
        templater = Templater(Path(self.link_dir.name), host_config)
        templater.set_color('coolcolor')
        active_color_path = Path(self.link_dir.name) / 'color.yaml'
        self.assertEqual(  # this is maybe questionable
                os.readlink(active_color_path),
                Path(self.color_dir.name) / 'coolcolor.yaml')

    def test_template(self):
        '''Test templating a string.'''
        raise unittest.SkipTest

    def test_themecolorcache_uncached(self):
        ''''''
        raise unittest.SkipTest

    def test_themecolorcache_cached_clean(self):
        ''''''
        raise unittest.SkipTest

    def test_themecolorcache_cached_dirty(self):
        ''''''
        raise unittest.SkipTest
