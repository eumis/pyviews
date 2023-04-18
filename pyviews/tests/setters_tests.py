import unittest
from importlib import import_module
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import call as call_mock

from injectool import add_singleton, use_container
from pytest import mark, raises

from pyviews.core.rendering import InstanceNode, Node
from pyviews.core.xml import XmlNode
from pyviews.setters import Args, call, call_args, import_global, inject_global, set_global


@mark.parametrize('node, key, value, expected', [
    (Node(XmlNode('', '')), 'key', 'unittest', unittest),
    (Node(XmlNode('', '')), 'anotherKey', 'unittest.TestCase', TestCase),
    (Node(XmlNode('', '')), 'someKey', 'importlib.import_module', import_module)
]) # yapf: disable
def test_import_global(node, key, value, expected):
    """should import path and add it to node globals"""
    import_global(node, key, value)

    assert node.node_globals[key] == expected


@mark.parametrize('node, key, value', [
    (Node(XmlNode('', '')), 'key', 'value'),
    (Node(XmlNode('', '')), 'key', None),
    (Node(XmlNode('', '')), 'key', 1)
]) # yapf: disable
def test_set_global(node, key, value):
    """should add value to node globals"""
    set_global(node, key, value)

    assert node.node_globals[key] == value


@mark.parametrize('node, global_key, inject_key, value', [
    (Node(XmlNode('', '')), 'global_key', 'inject_key', 1),
    (Node(XmlNode('', '')), 'global_key', 'inject_key', '1'),
    (Node(XmlNode('', '')), 'glob_ar', 'array', [])
]) # yapf: disable
def test_inject_global(node, global_key, inject_key, value):
    """should inject value to node globals"""
    with use_container():
        add_singleton(inject_key, value)
        inject_global(node, global_key, inject_key)

    assert node.node_globals[global_key] == value


class TestNode(Node):

    def __init__(self):
        super().__init__(XmlNode('', ''))
        self.mocked_method = Mock()


class TestInstanceNode(InstanceNode):

    def __init__(self):
        instance = Mock(one = Mock(), two = Mock())
        super().__init__(instance, XmlNode('', ''))
        self.one = Mock()


class CallTests:

    @staticmethod
    @mark.parametrize('args', [
        call_args(None),
        call_args([]),
        call_args(()),
        call_args("value"),
        call_args(1),
        call_args([1]),
        call_args(None),
        call_args(1, "value"),
        call_args(1, "value", {}),
        call_args(1, "value", key='value'),
        call_args([1], key='value', value='other value')
    ]) # yapf: disable
    def test_calls_node_method(args: Args):
        """call setter should call node instance method"""
        node = TestNode()

        call(node, 'mocked_method', args)

        assert node.mocked_method.call_args == call_mock(*args.args, **args.kwargs)

    @staticmethod
    @mark.parametrize('args', [
        call_args(None),
        call_args([]),
        call_args(()),
        call_args("value"),
        call_args(1),
        call_args([1]),
        call_args(None),
        call_args(1, "value"),
        call_args(1, "value", {}),
        call_args(1, "value", key='value'),
        call_args([1], key='value', value='other value')
    ]) # yapf: disable
    def test_calls_instance_method(args: Args):
        """call setter should call node instance method"""
        node = TestInstanceNode()

        call(node, 'two', args)

        assert node.instance.two.call_args == call_mock(*args.args, **args.kwargs)

    @staticmethod
    @mark.parametrize(
        'node, method', [(TestNode(), 'some_method'), (InstanceNode('value', XmlNode('', '')), 'instance_method')]
    )
    def test_raises_if_method_not_found(node: Node, method: str):
        with raises(AttributeError):
            call(node, method, call_args())

    @staticmethod
    def test_uses_node_method_first():
        node = TestInstanceNode()

        call(node, 'one', call_args())

        assert node.one.called
        assert not node.instance.mocked_method.called
