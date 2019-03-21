#pylint: disable=missing-docstring, invalid-name

import unittest
from unittest import TestCase
from importlib import import_module
from pyviews.testing import case
from .reflection import import_path

class import_path_tests(TestCase):
    @case('unittest', unittest)
    @case('unittest.TestCase', TestCase)
    @case('importlib.import_module', import_module)
    def test_import_path(self, path, expected):
        self.assertEqual(import_path(path), expected, 'import_path imports wrong item')

    @case(None)
    @case('')
    @case('    ')
    @case('asdf')
    @case('unittest.asdf')
    def test_import_path_raises(self, invalid_path):
        msg = 'import_path should raise ImportError for invalid path ' + str(invalid_path)
        with self.assertRaises(ImportError, msg=msg):
            import_path(invalid_path)
