import unittest
from typing import Any
from unittest import TestCase
from importlib import import_module
from unittest.mock import call as call_args, Mock

from pyviews.testing import case
from pyviews.core import Node
from pyviews.ioc import scope, register_single
from pyviews.rendering.modifiers import import_global, set_global, inject_global, call


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


class TestNode:
    def __init__(self):
        self.mocked_method = Mock()


class CallModifierTests(TestCase):
    """call modifier tests"""

    @case(None, call_args())
    @case([], call_args())
    @case((), call_args())
    @case("value", call_args("value"))
    @case(1, call_args(1))
    @case([1], call_args(1))
    @case([None], call_args(None))
    @case([1, "value"], call_args(1, "value"))
    @case([1, "value", {}], call_args(1, "value", **{}))
    @case([1, "value", {'key': 'value'}], call_args(1, "value", **{'key': 'value'}))
    @case([1, "value", {'key': 1}, {'key': 'value'}], call_args(1, "value", {'key': 1}, **{'key': 'value'}))
    @case((1,), call_args(1))
    @case((None,), call_args(None))
    @case((1, "value"), call_args(1, "value"))
    @case((1, "value", {}), call_args(1, "value", **{}))
    @case((1, "value", {'key': 'value'}), call_args(1, "value", **{'key': 'value'}))
    @case((1, "value", {'key': 1}, {'key': 'value'}), call_args(1, "value", {'key': 1}, **{'key': 'value'}))
    def test_calls_node_method(self, value: Any, expected_args: call_args):
        node = TestNode()

        call(node, 'mocked_method', value)

        msg = 'should call node method'
        self.assertEqual(expected_args, node.mocked_method.call_args, msg=msg)
