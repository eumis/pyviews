from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews.core.binding import BindableDict
from pyviews.core.rendering import Node, NodeGlobals
from pyviews.core.xml import XmlNode


class NodeGlobalsTests:

    @staticmethod
    @mark.parametrize('parent', [
        ({'key': 'value'}),
        (BindableDict({'key': 'value'})),
        (NodeGlobals({'key': 'value', 'two': 1}))
    ]) # yapf: disable
    def test_uses_parent_values(parent):
        """should use parent values"""
        node_globals = NodeGlobals(parent)

        assert node_globals == parent

    @staticmethod
    @mark.parametrize('parent, key, value', [
        (BindableDict({'key': 'value'}), 'key', 1),
        (NodeGlobals({'key': 'value', 'two': 1}), 'two', 'new value')
    ]) # yapf: disable
    def test_listens_to_parent_changes(parent, key, value):
        """should use updated parent values"""
        node_globals = NodeGlobals(parent)

        parent[key] = value
        assert node_globals[key] == value

    @staticmethod
    @mark.parametrize('parent, key, value, parent_value', [
        (BindableDict({'key': 'value'}), 'key', 1, 2),
        (NodeGlobals({'key': 'value', 'two': 1}), 'two', 'new value', 'new parent value')
    ]) # yapf: disable
    def test_uses_own_value(parent, key, value, parent_value):
        """should use own values"""
        node_globals = NodeGlobals(parent)

        node_globals[key] = value
        parent[key] = parent_value
        assert node_globals[key] == value

    @staticmethod
    @mark.parametrize('parent, key, value, parent_value', [
        (BindableDict({'key': 'value'}), 'key', 1, 2),
        (NodeGlobals({'key': 'value', 'two': 1}), 'two', 'new value', 'new parent value')
    ]) # yapf: disable
    def test_del_removes_own_value(parent, key, value, parent_value):
        """should pop own item"""
        node_globals = NodeGlobals(parent)
        node_globals[key] = value
        parent[key] = parent_value
        callback = Mock()
        node_globals.observe(key, callback)

        del node_globals[key]

        assert node_globals[key] == parent_value
        assert callback.call_args == call(parent_value, value)

    @staticmethod
    @mark.parametrize('parent, key', [
        (BindableDict({'key': 'value'}), 'key'),
        (NodeGlobals({'key': 'value', 'two': 1}), 'key')
    ]) # yapf: disable
    def test_del_raises_when_key_is_not_own(parent, key):
        """should raise KeyError when key is not presented"""
        node_globals = NodeGlobals(parent)

        with raises(KeyError):
            del node_globals[key]
        assert node_globals[key] == parent[key]

    @staticmethod
    @mark.parametrize('parent, key, value, parent_value', [
        (BindableDict({'key': 'value'}), 'key', 1, 2),
        (NodeGlobals({'key': 'value', 'two': 1}), 'two', 'new value', 'new parent value')
    ]) # yapf: disable
    def test_pop_removes_own_value(parent, key, value, parent_value):
        """should pop own item"""
        node_globals = NodeGlobals(parent)
        node_globals[key] = value
        parent[key] = parent_value
        callback = Mock()
        node_globals.observe(key, callback)

        popped_value = node_globals.pop(key)

        assert popped_value == value
        assert node_globals[key] == parent_value
        assert callback.call_args == call(parent_value, value)

    @staticmethod
    @mark.parametrize('parent, key', [
        (BindableDict({'key': 'value'}), 'key'),
        (NodeGlobals({'key': 'value', 'two': 1}), 'key')
    ]) # yapf: disable
    def test_pop_does_nothing(parent, key):
        """should return default value when key is not presented"""
        node_globals = NodeGlobals(parent)
        callback = Mock()
        node_globals.observe(key, callback)

        popped_value = node_globals.pop(key)

        assert popped_value is None
        assert node_globals[key] == parent[key]
        assert not callback.called


@fixture
def node_fixture(request):
    xml_node = XmlNode('namespace', 'root')
    request.cls.xml_node = xml_node
    request.cls.node = Node(xml_node)


@mark.usefixtures('node_fixture')
class NodeTests:
    """Node class tests"""

    xml_node: XmlNode
    node: Node

    def test_init_xml_node(self):
        """__init__() should set xml_node"""
        assert self.node.xml_node == self.xml_node

    @staticmethod
    @mark.parametrize('node_globals', [
        None,
        NodeGlobals(),
        NodeGlobals({'one': 1})
    ]) # yapf: disable
    def test_init_setup_globals(node_globals: NodeGlobals):
        """__init__() should setup node_globals"""
        node = Node(Mock(), node_globals)

        assert node.node_globals is not None
        if node_globals is not None:
            assert node.node_globals == node_globals

    @staticmethod
    @mark.parametrize('node_globals', [
        None,
        NodeGlobals(),
        NodeGlobals({'one': 1})
    ]) # yapf: disable
    def test_adds_self_to_globals(node_globals: NodeGlobals):
        """__init__() should add self to node_globals"""
        node = Node(Mock(), node_globals)

        assert node == node.node_globals['node']

    @mark.parametrize('key, value', [
        ('key', 1),
        ('key', None),
        ('key', 'value'),
        ('setter', 'value'),
    ]) # yapf: disable
    def test_setattr_sets_property(self, key, value):
        """__setattr__() should set property from properties"""
        # node.properties = {key: Property(key)}

        setattr(self.node, key, value)
        actual = getattr(self.node, key, value)

        assert actual == value

    @staticmethod
    @mark.parametrize('bindings_count', [1, 3])
    def test_destroy_destroys_bindings(bindings_count):
        """destroy() should destroy all node's bindings"""
        node = Node(Mock())
        bindings = []
        for _ in range(bindings_count):
            binding = Mock()
            binding.destroy = Mock()
            node.add_binding(binding)
            bindings.append(binding)

        node.destroy()

        for binding in bindings:
            assert binding.destroy.called

    @staticmethod
    @mark.parametrize('bindings_count', [1, 3])
    def test_destroy_destroys_children(bindings_count):
        """destroy() should destroy children"""
        node = Node(Mock())
        children = []
        for _ in range(bindings_count):
            child = Mock()
            child.destroy = Mock()
            node.add_child(child)
            children.append(child)

        node.destroy()

        for child in children:
            assert child.destroy.called

    @staticmethod
    def test_destroy_calls_on_destroy():
        """destroy() should call on_destroy"""
        node = Node(Mock())
        node.on_destroy = Mock()

        node.destroy()

        assert node.on_destroy.call_args == call(node)
