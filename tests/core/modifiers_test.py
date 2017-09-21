import unittest
from unittest import TestCase, main
from importlib import import_module
from tests.utility import case
from tests.mock import SomeObject
from pyviews.core.modifiers import import_global
from pyviews.core.parsing import Node

class TestModifiers(TestCase):
    @case(Node(None, None), ('key', 'unittest'), unittest)
    @case(Node(None, None), ('anotherKey', 'unittest.TestCase'), TestCase)
    @case(Node(None, None), ('someKey', 'importlib.import_module'), import_module)
    @case(Node(None, None), ('key', 'tests.core.reflection_test.SomeObject'), SomeObject)
    def test_import_global(self, node, attr, expected):
        import_global(node, attr)
        msg = 'import_global should import path and add it to node''s globals'
        self.assertEqual(node.globals[attr[0]], expected, msg)

    @case(Node(None, None), ('key', None))
    @case(Node(None, None), ('anotherKey', ''))
    @case(Node(None, None), ('someKey', '   '))
    @case(Node(None, None), ('key', 'asdf'))
    @case(Node(None, None), ('key', 'unittest.asdf'))
    def test_import_global_invalid_path(self, node, attr):
        import_global(node, attr)
        msg = 'import_global should set None to globals for invalid path'
        self.assertEqual(node.globals[attr[0]], None, msg)

if __name__ == '__main__':
    main()
