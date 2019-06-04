from unittest.mock import Mock, call

from pytest import fixture, mark

from pyviews.core.node import Node, Property
from pyviews.core.observable import InheritedDict
from pyviews.core.xml import XmlNode


@fixture
def node_fixture():
    xml_node = XmlNode('namespace', 'root')
    return xml_node, Node(xml_node)


class NodeTests:
    @staticmethod
    def test_init_xml_node(node_fixture):
        """__init__() should set xml_node"""
        xml_node, node = node_fixture

        assert node.xml_node == xml_node

    @mark.parametrize('node_globals', [
        None,
        InheritedDict(),
        InheritedDict({'one': 1})
    ])
    def test_init_setup_globals(self, node_globals: InheritedDict):
        """__init__() should setup node_globals"""
        node = Node(Mock(), node_globals)

        assert node.node_globals is not None
        if node_globals is not None:
            assert node.node_globals == node_globals

    @mark.parametrize('node_globals', [
        None,
        InheritedDict(),
        InheritedDict({'one': 1})
    ])
    def test_adds_self_to_globals(self, node_globals: InheritedDict):
        """__init__() should add self to node_globals"""
        node = Node(Mock(), node_globals)

        assert node == node.node_globals['node']

    @mark.parametrize('key, value', [
        ('key', 1),
        ('key', None),
        ('key', 'value'),
        ('setter', 'value'),
    ])
    def test_setattr_sets_property(self, node_fixture, key, value):
        """__setattr__() should set property from properties"""
        node = node_fixture[-1]
        # node.properties = {key: Property(key)}

        setattr(node, key, value)
        actual = getattr(node, key, value)

        assert actual == value

    @staticmethod
    def test_setattr_sets_own_property():
        """__setattr__() should set own properties"""
        node = Node(Mock())

        def setter(*_): pass

        node.attr_setter = setter

        assert node.attr_setter == setter

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


class PropertyTests:
    @staticmethod
    def test_default_get():
        """get() should return None by default"""
        prop = Property('')

        actual = prop.get()

        assert actual is None

    @mark.parametrize('value', [
        None,
        1,
        object(),
        'value'
    ])
    def test_get_returns_set_value(self, value):
        """get() should return value"""
        prop = Property('')
        prop.set(value)

        actual = prop.get()

        assert actual == value

    @mark.parametrize('node', [
        None,
        Node(Mock())
    ])
    def test_set_calls_setter(self, node):
        """set() should pass node and value to setter"""
        setter_mock = Mock()

        def setter(setter_node, val):
            setter_mock(setter_node, val)
            return val

        prop = Property('', setter, node)
        value = 1

        prop.set(value)

        assert setter_mock.call_args == call(node, value)

    @mark.parametrize('previous, value', [
        (1, None),
        (None, 1),
        (object(), object()),
        ('value', 'another value')
    ])
    def test_set_calls_previous_setter(self, previous, value):
        """set() should pass node, value and previous value to setter"""
        setter_mock = Mock()

        def setter(setter_node, val):
            setter_mock(setter_node, val)
            return val

        prop = Property('', setter)

        prop.set(previous)
        prop.set(value)

        assert setter_mock.call_args_list[0], call(None, previous, None)
        assert setter_mock.call_args_list[1], call(None, value, previous)

    @staticmethod
    @mark.parametrize('node', [
        None,
        Node(Mock())
    ])
    def test_new_creates_property(node):
        """new() should create same property for passed node"""
        setter_mock = Mock()

        def setter(setter_node, val):
            setter_mock(setter_node, val)
            return val

        prop = Property('', setter)
        value = 1

        actual_prop = prop.new(node)
        actual_prop.set(value)

        assert actual_prop != prop
        assert setter_mock.call_args, call(node, value)
