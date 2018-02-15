from unittest import TestCase, main
from tests.utility import case
from tests.mock import some_modifier
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node
from pyviews.core import parsing, ioc

class TestParseNode(TestCase):
    def setUp(self):
        xml_node = XmlNode('pyviews.core.node', 'Node')
        self.parent_node = parsing.Node(xml_node)

        self.xml_node = XmlNode('pyviews.core.node', 'Node')

    def test_parse(self):
        self.parent_node.globals['some_key'] = 'some value'

        node = parsing.parse(self.xml_node, parsing.NodeArgs(self.xml_node, self.parent_node))

        msg = 'parse should init node with right passed xml_node'
        self.assertIsInstance(node, Node, msg=msg)

        msg = 'parse should init node with passed parent'
        self.assertEqual(node.globals['some_key'], 'some value', msg=msg)

class SomeObject:
    def __init__(self):
        pass

class TestParseObjectNode(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('tests.core.parsing_test', 'SomeObject')

    def test_parse_raises(self):
        msg = 'parse should raise error if method "convert_to_node" is not registered'
        with self.assertRaises(NotImplementedError, msg=msg):
            parsing.parse(self.xml_node, parsing.NodeArgs(self.xml_node))

class TestGetModifier(TestCase):
    @case(None, '', ioc.CONTAINER.get('set_attr'))
    @case(None, 'attr_name', ioc.CONTAINER.get('set_attr'))
    @case('tests.core.parsing_test.some_modifier', '', some_modifier)
    @case('tests.core.parsing_test.some_modifier', 'attr_name', some_modifier)
    def test_get_modifier(self, namespace, name, expected):
        xml_attr = XmlAttr(name, '', namespace)
        actual = parsing.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @case('', '')
    @case('', 'attr_name')
    @case('tests.core.parsing_test.some_modifier_not', 'attr_name')
    def test_get_modifier_raises(self, namespace, name):
        msg = 'get_modifier should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr(name, '', namespace)
            parsing.get_modifier(xml_attr)

class TestExpressions(TestCase):
    @case('{asdf}', True)
    @case('once:{asdf}', True)
    @case('oneway:{asdf}', True)
    @case('twoways:{asdf}', True)
    @case('{{asdf}}', True)
    @case('twoways:{{asdf}}', True)
    @case('once:{{asdf}}', True)
    @case('oneway:{{asdf}}', True)
    @case('twoways:{conv:{asdf}}', True)
    @case('twoways:{asdf}', True)
    @case('twoways:{asdf}', True)
    @case('oneway{asdf}', False)
    @case(':{asdf}', False)
    @case('{asdf', False)
    @case('once:{asdf', False)
    @case('asdf}', False)
    @case(' {asdf}', False)
    @case('once: {asdf}', False)
    def test_is_code_expression(self, expr, expected):
        self.assertEqual(parsing.is_code_expression(expr), expected)

    @case('{asdf}', ('oneway', 'asdf'))
    @case('once:{asdf}', ('once', 'asdf'))
    @case('oneway:{asdf}', ('oneway', 'asdf'))
    @case('twoways:{asdf}', ('twoways', 'asdf'))
    @case('{{asdf}}', ('twoways', '{asdf}'))
    @case('{to_int:{asdf}}', ('twoways', 'to_int:{asdf}'))
    @case('twoways:{{asdf}}', ('twoways', '{asdf}'))
    @case('oneway:{{asdf}}', ('oneway', '{asdf}'))
    @case('twoways:{to_int:{asdf}}', ('twoways', 'to_int:{asdf}'))
    def test_parse_expression(self, expr, expected):
        self.assertEqual(parsing.parse_expression(expr), expected)

if __name__ == '__main__':
    main()
