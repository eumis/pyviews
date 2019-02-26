#pylint: disable=missing-docstring

import unittest
from unittest import TestCase
from importlib import import_module
from pyviews.testing import case
from pyviews.core import Node
from pyviews.core.ioc import scope, register_single
from .modifiers import import_global, set_global, inject_global

class ModifiersTests(TestCase):
    @case(Node(None, None), 'key', 'unittest', unittest)
    @case(Node(None, None), 'anotherKey', 'unittest.TestCase', TestCase)
    @case(Node(None, None), 'someKey', 'importlib.import_module', import_module)
    def test_import_global(self, node, key, value, expected):
        import_global(node, key, value)
        msg = 'import_global should import path and add it to node''s globals'
        self.assertEqual(node.node_globals[key], expected, msg)

    @case(Node(None, None), 'key', 'value')
    @case(Node(None, None), 'key', None)
    @case(Node(None, None), 'key', 1)
    def test_set_global(self, node, key, value):
        set_global(node, key, value)
        msg = 'set_global should add value to global'
        self.assertEqual(node.node_globals[key], value, msg)

    @scope('test_inject_global')
    @case(Node(None, None), 'global_key', 'inject_key', 1)
    @case(Node(None, None), 'global_key', 'inject_key', '1')
    @case(Node(None, None), 'glob_ar', 'array', [])
    def test_inject_global(self, node, global_key, inject_key, value):
        register_single(inject_key, value)
        inject_global(node, global_key, inject_key)
        msg = 'inject_global should get value by key from container and add it to node''s globals'
        self.assertEqual(node.node_globals[global_key], value, msg)
