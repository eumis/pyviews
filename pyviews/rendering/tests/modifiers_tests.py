import unittest
from importlib import import_module
from typing import Any
from unittest import TestCase
from unittest.mock import call as call_args, Mock

from pytest import mark, raises

from pyviews.core import Node, XmlNode, InstanceNode
from injectool import register_single, Scope
from pyviews.rendering.modifiers import import_global, set_global, inject_global, call


@mark.parametrize('node, key, value, expected', [
    (Node(XmlNode('', '')), 'key', 'unittest', unittest),
    (Node(XmlNode('', '')), 'anotherKey', 'unittest.TestCase', TestCase),
    (Node(XmlNode('', '')), 'someKey', 'importlib.import_module', import_module)
])
def test_import_global(node, key, value, expected):
    """should import path and add it to node globals"""
    import_global(node, key, value)

    assert node.node_globals[key] == expected


@mark.parametrize('node, key, value', [
    (Node(XmlNode('', '')), 'key', 'value'),
    (Node(XmlNode('', '')), 'key', None),
    (Node(XmlNode('', '')), 'key', 1)
])
def test_set_global(node, key, value):
    """should add value to node globals"""
    set_global(node, key, value)

    assert node.node_globals[key] == value


@mark.parametrize('node, global_key, inject_key, value', [
    (Node(XmlNode('', '')), 'global_key', 'inject_key', 1),
    (Node(XmlNode('', '')), 'global_key', 'inject_key', '1'),
    (Node(XmlNode('', '')), 'glob_ar', 'array', [])
])
def test_inject_global(node, global_key, inject_key, value):
    """should inject value to node globals"""
    with Scope('test_inject_global'):
        register_single(inject_key, value)
        inject_global(node, global_key, inject_key)

    assert node.node_globals[global_key] == value


class TestNode(Node):
    def __init__(self):
        super().__init__(XmlNode('', ''))
        self.mocked_method = Mock()


class TestInstanceNode(InstanceNode):
    def __init__(self):
        instance = Mock(mocked_method=Mock())
        super().__init__(instance, XmlNode('', ''))


class CallTests:
    @staticmethod
    @mark.parametrize('value, expected_args', [
        (None, call_args()),
        ([], call_args()),
        ((), call_args()),
        ("value", call_args("value")),
        (1, call_args(1)),
        ([1], call_args(1)),
        ([None], call_args(None)),
        ([1, "value"], call_args(1, "value")),
        ([1, "value", {}], call_args(1, "value", **{})),
        ([1, "value", {'key': 'value'}], call_args(1, "value", **{'key': 'value'})),
        ([1, "value", {'key': 1}, {'key': 'value'}], call_args(1, "value", {'key': 1}, **{'key': 'value'})),
        ((1,), call_args(1)),
        ((None,), call_args(None)),
        ((1, "value"), call_args(1, "value")),
        ((1, "value", {}), call_args(1, "value", **{})),
        ((1, "value", {'key': 'value'}), call_args(1, "value", **{'key': 'value'})),
        ((1, "value", {'key': 1}, {'key': 'value'}), call_args(1, "value", {'key': 1}, **{'key': 'value'}))
    ])
    def test_calls_node_method(value: Any, expected_args: call_args):
        """call modifier should call node method"""
        node = TestNode()

        call(node, 'mocked_method', value)

        assert expected_args == node.mocked_method.call_args

    @staticmethod
    @mark.parametrize('value, expected_args', [
        (None, call_args()),
        ([], call_args()),
        ((), call_args()),
        ("value", call_args("value")),
        (1, call_args(1)),
        ([1], call_args(1)),
        ([None], call_args(None)),
        ([1, "value"], call_args(1, "value")),
        ([1, "value", {}], call_args(1, "value", **{})),
        ([1, "value", {'key': 'value'}], call_args(1, "value", **{'key': 'value'})),
        ([1, "value", {'key': 1}, {'key': 'value'}], call_args(1, "value", {'key': 1}, **{'key': 'value'})),
        ((1,), call_args(1)),
        ((None,), call_args(None)),
        ((1, "value"), call_args(1, "value")),
        ((1, "value", {}), call_args(1, "value", **{})),
        ((1, "value", {'key': 'value'}), call_args(1, "value", **{'key': 'value'})),
        ((1, "value", {'key': 1}, {'key': 'value'}), call_args(1, "value", {'key': 1}, **{'key': 'value'}))
    ])
    def test_calls_instance_method(value: Any, expected_args: call_args):
        """call modifier should call node instance method"""
        node = TestInstanceNode()

        call(node, 'mocked_method', value)

        assert expected_args == node.instance.mocked_method.call_args

    @staticmethod
    @mark.parametrize('node, method', [
        (TestNode(), 'some_method'),
        (InstanceNode('value', XmlNode('', '')), 'instance_method')
    ])
    def test_raises_if_method_not_found(node: Node, method: str):
        with raises(AttributeError):
            call(node, method, 'value')

    @staticmethod
    def test_uses_node_method_first():
        node = TestInstanceNode()
        node.mocked_method = Mock()

        call(node, 'mocked_method', 'value')

        assert node.mocked_method.called
        assert not node.instance.mocked_method.called
