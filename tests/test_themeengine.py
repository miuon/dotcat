'''Test ThemeEngine functions'''
import unittest

from modot.themeengine import ThemeEngine

class TestThemeEngine(unittest.TestCase):
    '''Test the ThemeEngine'''

    def test_noop_passes(self):
        '''Dummy test, check that ThemeEngine is ThemeEngine'''
        self.assertEqual(ThemeEngine.__name__, 'ThemeEngine')
