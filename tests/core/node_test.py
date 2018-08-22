from unittest import TestCase, main
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from pyviews.core.node import Node, setter, keysetter

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

class SettersTests(TestCase):
    @case('key', 'key', True)
    @case('key', 'Key', False)
    @case('key', 'KEY', False)
    @case('key', 'other key', False)
    def test_keysetter_filter_key(self, key, passed_key, called):
        setter_mock = Mock()
        decorated = keysetter(key)(setter_mock)

        returned = decorated(None, passed_key, None)

        msg = 'keysetter should decorated function to be called only for passed key'
        self.assertEqual(setter_mock.called, called, msg)

        msg = 'keysetter should decorated function to return True for passed key'
        self.assertEqual(returned, called, msg)

    def test_setter_returns_true(self):
        setter_mock = Mock()
        decorated = setter(setter_mock)

        actual = decorated(None, None, None)

        msg = 'setter should decorate function that returns true'
        self.assertTrue(actual, msg)

    def test_setter_calls_decorated(self):
        setter_mock = Mock()
        decorated = setter(setter_mock)

        decorated(None, None, None)

        msg = 'setter should decorate function to call it'
        self.assertTrue(setter_mock.called, msg)

if __name__ == '__main__':
    main()
