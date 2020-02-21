from unittest.mock import Mock, call

from pytest import fixture, mark

from pyviews.core.rendering import Node
from pyviews.core.observable import InheritedDict
from pyviews.core import XmlNode


@fixture
def node_fixture(request):
    xml_node = XmlNode('namespace', 'root')
    request.cls.xml_node = xml_node
    request.cls.node = Node(xml_node)


@mark.usefixtures('node_fixture')
class NodeTests:
    def test_init_xml_node(self):
        """__init__() should set xml_node"""
        assert self.node.xml_node == self.xml_node

    @staticmethod
    @mark.parametrize('node_globals', [
        None,
        InheritedDict(),
        InheritedDict({'one': 1})
    ])
    def test_init_setup_globals(node_globals: InheritedDict):
        """__init__() should setup node_globals"""
        node = Node(Mock(), node_globals)

        assert node.node_globals is not None
        if node_globals is not None:
            assert node.node_globals == node_globals

    @staticmethod
    @mark.parametrize('node_globals', [
        None,
        InheritedDict(),
        InheritedDict({'one': 1})
    ])
    def test_adds_self_to_globals(node_globals: InheritedDict):
        """__init__() should add self to node_globals"""
        node = Node(Mock(), node_globals)

        assert node == node.node_globals['node']

    @mark.parametrize('key, value', [
        ('key', 1),
        ('key', None),
        ('key', 'value'),
        ('setter', 'value'),
    ])
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
