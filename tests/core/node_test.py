from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.testing import case
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from pyviews.core.node import Node, Property

class NodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('namespace', 'root')
        self.node = Node(self.xml_node)

    def test_init_xml_node(self):
        node = Node(self.xml_node)

        msg = 'Node should inititalise properties'
        self.assertEqual(node.xml_node, self.xml_node, msg)

    @case(None, {})
    @case(InheritedDict({'one': 1}), {'one': 1})
    def test_init_setup_globals(self, globals: InheritedDict, expected_dict):
        node = Node(self.xml_node, globals)

        msg = 'init should setup globals'
        self.assertIsNotNone(node.globals)

        msg = 'init should add node to globals'
        self.assertEqual(node, node.globals['node'], msg)

        msg = 'should inherit passed globals'
        self.assertDictContainsSubset(expected_dict, node.globals.to_dictionary(), msg)

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

        node.setter = setter

        msg = 'setattr should set own property if key not in properties'
        self.assertEqual(node.setter, setter, msg)

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


    @case(1, None)
    @case(None, 1)
    @case(object(), object())
    @case('value', 'another value')
    def test_set_calls_setter(self, previous, value):
        setter = Mock()
        setter.side_effect = lambda node, prev, val: val
        prop = Property('', setter)

        prop.set(previous)
        prop.set(value)

        msg = 'set should call setter with passed value and previous value'
        self.assertEqual(setter.call_args_list[0], call(None, None, previous), msg)
        self.assertEqual(setter.call_args_list[1], call(None, previous, value), msg)

    @case(None)
    @case(Node(Mock()))
    def test_set_calls_setter_with_passed_node(self, node):
        setter = Mock()
        prop = Property('', setter, node)
        value = 1

        prop.set(value)

        msg = 'set should call setter with passed node'
        self.assertEqual(setter.call_args, call(node, None, value), msg)

    @case(None)
    @case(Node(Mock()))
    def test_new_creates_property_with_node(self, node):
        setter = Mock()
        prop = Property('', setter)
        value = 1

        actual_prop = prop.new(node)
        actual_prop.set(value)

        msg = 'new should return new property for passed node'
        self.assertNotEqual(actual_prop, prop, msg)
        self.assertEqual(setter.call_args, call(node, None, value), msg)

    @case(None)
    @case(1)
    @case(object())
    @case('value')
    def test_set_sets_returned_setter_value(self, value):
        setter = Mock()
        setter.side_effect = lambda node, prev, val: val
        prop = Property('', setter)
        prop.set(value)

        actual = prop.get()

        msg = 'set should set value returned from setter'
        self.assertEqual(actual, value, msg)

if __name__ == '__main__':
    main()
