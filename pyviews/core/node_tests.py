#pylint: disable=missing-docstring

from unittest import TestCase
from unittest.mock import Mock, call
from pyviews.testing import case
from .xml import XmlNode
from .observable import InheritedDict
from .node import Node, Property

class NodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('namespace', 'root')
        self.node = Node(self.xml_node)

    def test_init_xml_node(self):
        node = Node(self.xml_node)

        msg = 'Node should inititalise properties'
        self.assertEqual(node.xml_node, self.xml_node, msg)

    @case(None)
    @case(InheritedDict())
    @case(InheritedDict({'one': 1}))
    def test_init_setup_globals(self, node_globals: InheritedDict):
        node = Node(self.xml_node, node_globals)

        msg = 'init should setup globals'
        self.assertIsNotNone(node.node_globals)

        msg = 'init should add node to globals'
        self.assertEqual(node, node.node_globals['node'], msg)

        msg = 'should use passed globals or create new one'
        expected_globals = node_globals if node_globals else node.node_globals
        self.assertEqual(expected_globals, node.node_globals, msg)

    @case('key', 1)
    @case('key', None)
    @case('key', 'value')
    @case('setter', 'value')
    def test_setattr_sets_property(self, key, value):
        node = Node(Mock())
        node.properties = {key: Property(key)}

        setattr(node, key, value)
        actual = getattr(node, key, value)

        msg = 'setattr should set property from properties'
        self.assertEqual(actual, value, msg)

    def test_setattr_sets_own_property(self):
        node = Node(Mock())
        setter = lambda *args: None

        node.attr_setter = setter

        msg = 'setattr should set own property if key not in properties'
        self.assertEqual(node.attr_setter, setter, msg)

    @case(1)
    @case(3)
    def test_destroy_destroys_bindings(self, bindings_count):
        node = Node(Mock())
        bindings = []
        for _ in range(bindings_count):
            binding = Mock()
            binding.destroy = Mock()
            node.add_binding(binding)
            bindings.append(binding)

        node.destroy()

        msg = 'destroy should destroy bindings'
        for binding in bindings:
            self.assertTrue(binding.destroy.called, msg)

    @case(1)
    @case(3)
    def test_destroy_destroys_children(self, bindings_count):
        node = Node(Mock())
        children = []
        for _ in range(bindings_count):
            child = Mock()
            child.destroy = Mock()
            node.add_child(child)
            children.append(child)

        node.destroy()

        msg = 'destroy should destroy bindings'
        for child in children:
            self.assertTrue(child.destroy.called, msg)

    def test_destroy_calls_on_destroy(self):
        node = Node(Mock())
        node.on_destroy = Mock()

        node.destroy()

        msg = 'destroy should call on_destroy with passed node'
        self.assertEqual(node.on_destroy.call_args, call(node), msg)

class PropertyTests(TestCase):
    def test_default_get(self):
        prop = Property('')

        actual = prop.get()

        msg = 'get by default should return None'
        self.assertIsNone(actual, msg)

    @case(None)
    @case(1)
    @case(object())
    @case('value')
    def test_get_returns_set_value(self, value):
        prop = Property('')
        prop.set(value)

        actual = prop.get()

        msg = 'get should return set value'
        self.assertEqual(actual, value, msg)

    @case(None)
    @case(Node(Mock()))
    def test_set_calls_setter_with_passed_node_and_value(self, node):
        setter_mock = Mock()
        setter = lambda node, val: (val, setter_mock(node, val))[0]
        prop = Property('', setter, node)
        value = 1

        prop.set(value)

        msg = 'set should call setter with passed node'
        self.assertEqual(setter_mock.call_args, call(node, value), msg)

    @case(1, None)
    @case(None, 1)
    @case(object(), object())
    @case('value', 'another value')
    def test_set_calls_setter_with_previous(self, previous, value):
        setter_mock = Mock()
        setter = lambda node, val, prev: (val, setter_mock(node, val, prev))[0]
        prop = Property('', setter)

        prop.set(previous)
        prop.set(value)

        msg = 'set should call setter with passed value and previous value'
        self.assertEqual(setter_mock.call_args_list[0], call(None, previous, None), msg)
        self.assertEqual(setter_mock.call_args_list[1], call(None, value, previous), msg)

    @case(None)
    @case(Node(Mock()))
    def test_new_creates_property_with_node(self, node):
        setter_mock = Mock()
        setter = lambda node, val: (val, setter_mock(node, val))[0]
        prop = Property('', setter)
        value = 1

        actual_prop = prop.new(node)
        actual_prop.set(value)

        msg = 'new should return new property for passed node'
        self.assertNotEqual(actual_prop, prop, msg)
        self.assertEqual(setter_mock.call_args, call(node, value), msg)
