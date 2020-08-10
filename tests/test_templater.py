'''Test theme/color setting and templating.'''
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from modot.hostconfig import HostConfig
from modot.templater import LinkMalformedError, Templater


class TestTemplaterThemes(unittest.TestCase):
    '''Test templater methods for manipulating the active theme.'''

    def setUp(self):
        '''Set up some temp directories for test.'''
        self.link_dir = TemporaryDirectory()
        self.theme_dir = TemporaryDirectory()

    def tearDown(self):
        self.link_dir.cleanup()
        self.theme_dir.cleanup()

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

    def test_set_theme(self):
        '''Test setting the active theme.'''
        host_config = HostConfig(
            Path(self.theme_dir.name), None)
        templater = Templater(Path(self.link_dir.name), host_config)
        templater.set_theme('cooltheme')
        active_theme_path = Path(self.link_dir.name) / 'theme.yaml'
        self.assertEqual(  # this is maybe questionable
            Path(os.readlink(active_theme_path)),
            Path(self.theme_dir.name) / 'cooltheme.yaml')


class TestTemplaterColors(unittest.TestCase):
    '''Test templater methods for manipulating the active color.'''

    def setUp(self):
        '''Set up some temp directories for test.'''
        self.link_dir = TemporaryDirectory()
        self.color_dir = TemporaryDirectory()

    def tearDown(self):
        self.link_dir.cleanup()
        self.color_dir.cleanup()

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

    def test_set_color(self):
        '''Test setting the active color.'''
        host_config = HostConfig(
            Path(self.color_dir.name), Path(self.color_dir.name))
        templater = Templater(Path(self.link_dir.name), host_config)
        templater.set_color('coolcolor')
        active_color_path = Path(self.link_dir.name) / 'color.yaml'
        self.assertEqual(  # this is maybe questionable
            Path(os.readlink(active_color_path)),
            Path(self.color_dir.name) / 'coolcolor.yaml')


class TestTemplaterTemplate(unittest.TestCase):
    '''Test the templater template method/related functionality.'''
    def setUp(self):
        '''Set up some temp directories for test.'''
        self.link_dir_handle = TemporaryDirectory()
        self.link_dir = Path(self.link_dir_handle.name)
        self.theme_dir_handle = TemporaryDirectory()
        self.theme_dir = Path(self.theme_dir_handle.name)
        self.color_dir_handle = TemporaryDirectory()
        self.color_dir = Path(self.color_dir_handle.name)

    def tearDown(self):
        self.link_dir_handle.cleanup()
        self.theme_dir_handle.cleanup()
        self.color_dir_handle.cleanup()

    def test_template(self):
        '''Test templating a string.'''
        theme_path = self.theme_dir/'main.yaml'
        color_path = self.color_dir/'main.yaml'
        (self.link_dir/'theme.yaml').symlink_to(theme_path)
        (self.link_dir/'color.yaml').symlink_to(color_path)
        theme_path.write_text('theme: cooltheme')
        color_path.write_text('color: coolcolor')
        host_cfg = HostConfig(self.theme_dir, self.color_dir)
        templater = Templater(self.link_dir, host_cfg)
        out_str = templater.template('theme: {{theme}}\ncolor: {{color}}')
        self.assertEqual(out_str, 'theme: cooltheme\ncolor: coolcolor')

    def test_template_conf_dne(self):
        '''Test templating a string.'''
        theme_path = self.theme_dir/'main.yaml'
        color_path = self.color_dir/'main.yaml'
        (self.link_dir/'theme.yaml').symlink_to(theme_path)
        (self.link_dir/'color.yaml').symlink_to(color_path)
        theme_path.write_text('theme: cooltheme')
        host_cfg = HostConfig(self.theme_dir, self.color_dir)
        templater = Templater(self.link_dir, host_cfg)
        with self.assertRaises(LinkMalformedError):
            templater.template('theme: {{theme}}\ncolor: {{color}}')

    def test_template_after_set_theme(self):
        '''Test that set_color changes the output even after first use.'''
        theme_path = self.theme_dir/'main.yaml'
        color_path = self.color_dir/'main.yaml'
        new_theme_path = self.theme_dir/'new.yaml'
        (self.link_dir/'theme.yaml').symlink_to(theme_path)
        (self.link_dir/'color.yaml').symlink_to(color_path)
        theme_path.write_text('theme: cooltheme')
        color_path.write_text('color: coolcolor')
        new_theme_path.write_text('theme: newtheme')
        host_cfg = HostConfig(self.theme_dir, self.color_dir)
        templater = Templater(self.link_dir, host_cfg)
        templater.template('theme: {{theme}}\ncolor: {{color}}')
        templater.set_theme('new')
        out_str = templater.template('theme: {{theme}}\ncolor: {{color}}')
        self.assertEqual(out_str, 'theme: newtheme\ncolor: coolcolor')

    def test_template_after_set_color(self):
        '''Test that set_color changes the output even after first use.'''
        theme_path = self.theme_dir/'main.yaml'
        color_path = self.color_dir/'main.yaml'
        new_color_path = self.color_dir/'new.yaml'
        (self.link_dir/'theme.yaml').symlink_to(theme_path)
        (self.link_dir/'color.yaml').symlink_to(color_path)
        theme_path.write_text('theme: cooltheme')
        color_path.write_text('color: coolcolor')
        new_color_path.write_text('color: newcolor')
        host_cfg = HostConfig(self.theme_dir, self.color_dir)
        templater = Templater(self.link_dir, host_cfg)
        templater.template('theme: {{theme}}\ncolor: {{color}}')
        templater.set_color('new')
        out_str = templater.template('theme: {{theme}}\ncolor: {{color}}')
        self.assertEqual(out_str, 'theme: cooltheme\ncolor: newcolor')
