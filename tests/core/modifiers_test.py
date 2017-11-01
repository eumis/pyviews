import unittest
from unittest import TestCase, main
from importlib import import_module
from tests.utility import case
from tests.mock import SomeObject
from pyviews.core.modifiers import import_global, set_global
from pyviews.core.parsing import Node

class TestModifiers(TestCase):
    @case(Node(None, None), 'key', 'unittest', unittest)
    @case(Node(None, None), 'anotherKey', 'unittest.TestCase', TestCase)
    @case(Node(None, None), 'someKey', 'importlib.import_module', import_module)
    @case(Node(None, None), 'key', 'tests.core.reflection_test.SomeObject', SomeObject)
    def test_import_global(self, node, key, value, expected):
        import_global(node, key, value)
        msg = 'import_global should import path and add it to node''s globals'
        self.assertEqual(node.globals[key], expected, msg)

    @case(Node(None, None), 'key', None)
    @case(Node(None, None), 'anotherKey', '')
    @case(Node(None, None), 'someKey', '   ')
    @case(Node(None, None), 'key', 'asdf')
    @case(Node(None, None), 'key', 'unittest.asdf')
    def test_import_global_invalid_path(self, node, key, value):
        import_global(node, key, value)
        msg = 'import_global should set None to globals for invalid path'
        self.assertEqual(node.globals[key], None, msg)

    @case(Node(None, None), 'key', 'value')
    @case(Node(None, None), 'key', None)
    @case(Node(None, None), 'key', 1)
    def test_set_global(self, node, key, value):
        set_global(node, key, value)
        msg = 'set_global should add value to global'
        self.assertEqual(node.globals[key], value, msg)

if __name__ == '__main__':
    main()
