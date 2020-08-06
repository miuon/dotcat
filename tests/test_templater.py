'''Test theme/color setting and templating.'''
import unittest

from modot.templater import Templater, _ThemeColorCache


class TestTemplater(unittest.TestCase):
    '''Test templater configuration and usage.'''

    def test_get_theme(self):
        '''Test getting theme with a correctly formatted link.'''

    def test_get_theme_no_link(self):
        '''Test getting theme with no link present.'''

    def test_get_theme_not_a_link(self):
        '''Test getting theme when the active path isn't a link.'''

    def test_get_theme_link_malformed(self):
        '''Test getting theme from a malformed link.'''

    def test_get_color(self):
        '''Test getting color with a correctly formatted link.'''

    def test_get_color_no_link(self):
        '''Test getting color with no link present.'''

    def test_get_color_not_a_link(self):
        '''Test getting color when the active path isn't a link.'''

    def test_get_color_link_malformed(self):
        '''Test getting color from a malformed link.'''

    def test_list_theme(self):
        '''Test listing the available themes.'''

    def test_list_theme_path_nonexistent(self):
        '''Test listing the available themes when the path does not exist.'''

    def test_list_color(self):
        '''Test listing the available colors.'''

    def test_list_color_path_nonexistent(self):
        '''Test listing the available colors when the path does not exist.'''

    def test_set_theme(self):
        '''Test setting the active theme.'''

    def test_set_theme_set_dirty(self):
        '''Test that setting the active theme sets the dirty bit.'''

    def test_set_color(self):
        '''Test setting the active color.'''

    def test_set_color_set_dirty(self):
        '''Test that setting the active color sets the dirty bit.'''

    def test_template(self):
        '''Test templating a string.'''

    def test_themecolorcache_uncached(self):
        ''''''

    def test_themecolorcache_cached_clean(self):
        ''''''

    def test_themecolorcache_cached_dirty(self):
        ''''''
