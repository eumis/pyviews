from unittest import TestCase, main
from tests.utility import case
from tests.mock import some_modifier
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, NodeArgs
from pyviews.core import ioc
from pyviews.rendering import core as parsing
from pyviews.rendering.dependencies import register_defaults

register_defaults()

class ParseNodeTests(TestCase):
    def setUp(self):
        xml_node = XmlNode('pyviews.core.node', 'Node')
        self.parent_node = Node(xml_node)

        self.xml_node = XmlNode('pyviews.core.node', 'Node')

    def test_parse(self):
        self.parent_node.globals['some_key'] = 'some value'

        node = parsing.parse(self.xml_node, NodeArgs(self.xml_node, self.parent_node))

        msg = 'parse should init node with right passed xml_node'
        self.assertIsInstance(node, Node, msg=msg)

        msg = 'parse should init node with passed parent'
        self.assertEqual(node.globals['some_key'], 'some value', msg=msg)

class SomeObject:
    def __init__(self):
        pass

class ParseObjectNodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('tests.rendering.core_test', 'SomeObject')

    def test_parse_raises(self):
        msg = 'parse should raise error if method "convert_to_node" is not registered'
        with self.assertRaises(NotImplementedError, msg=msg):
            parsing.parse(self.xml_node, parsing.NodeArgs(self.xml_node))

class GetModifierTests(TestCase):
    @case(None, '', ioc.CONTAINER.get('set_attr'))
    @case(None, 'attr_name', ioc.CONTAINER.get('set_attr'))
    @case('tests.rendering.core_test.some_modifier', '', some_modifier)
    @case('tests.rendering.core_test.some_modifier', 'attr_name', some_modifier)
    def test_get_modifier(self, namespace, name, expected):
        xml_attr = XmlAttr(name, '', namespace)
        actual = parsing.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @case('', '')
    @case('', 'attr_name')
    @case('tests.rendering.core_test.some_modifier_not', 'attr_name')
    def test_get_modifier_raises(self, namespace, name):
        msg = 'get_modifier should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr(name, '', namespace)
            parsing.get_modifier(xml_attr)


if __name__ == '__main__':
    main()
