import unittest
from unittest import TestCase, main
from importlib import import_module
from tests.utility import case
from tests.mock import SomeObject
from pyviews.core import reflection as tested

class TestReflection(TestCase):
    @case('package.module.name', ('package.module', 'name'))
    @case('package.module', ('package', 'module'))
    @case('package', ('package', None))
    def test_split_by_last_dot(self, name, expected):
        msg = 'split_by_last_dot returns wrong path parts'
        self.assertEqual(tested.split_by_last_dot(name), expected, msg)

    @case('unittest', unittest)
    @case('unittest.TestCase', TestCase)
    @case('importlib.import_module', import_module)
    @case('tests.core.reflection_test.SomeObject', SomeObject)
    def test_import_path(self, path, expected):
        self.assertEqual(tested.import_path(path), expected, 'import_path imports wrong item')

    @case(None)
    @case('')
    @case('    ')
    @case('asdf')
    @case('unittest.asdf')
    def test_import_path_raises(self, invalid_path):
        msg = 'import_path should raise ImportError for invalid path ' + str(invalid_path)
        with self.assertRaises(ImportError, msg=msg):
            tested.import_path(invalid_path)

def raise_(ex):
    raise ex

if __name__ == '__main__':
    main()
