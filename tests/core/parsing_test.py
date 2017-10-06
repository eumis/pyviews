from unittest import TestCase, main
from xml.etree import ElementTree as ET
from tests.utility import case
from tests.mock import some_modifier
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core import parsing, ioc

class TestNodeArgs(TestCase):
    def test_node_args(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = parsing.Node(xml_node)
        args = parsing.NodeArgs(xml_node, node)

        msg = 'NodeArgs should return XmlNode as args'
        self.assertEqual([xml_node], args.get_args(), msg)

        msg = 'NodeArgs should return parent as kargs'
        self.assertEqual({'parent_node': node}, args.get_kwargs(), msg)

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = parsing.Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

class TestParseNode(TestCase):
    def setUp(self):
        element = ET.fromstring('<Node xmlns="pyviews.core.parsing"/>')
        xml_node = XmlNode(element)
        self.parent_node = parsing.Node(xml_node)

        element = ET.fromstring('<Node xmlns="pyviews.core.parsing"/>')
        self.xml_node = XmlNode(element)

    def test_parse(self):
        self.parent_node.globals['some_key'] = 'some value'

        node = parsing.parse(self.xml_node, parsing.NodeArgs(self.xml_node, self.parent_node))

        msg = 'parse should init node with right passed xml_node'
        self.assertEqual(node.xml_node, self.xml_node, msg=msg)

        msg = 'parse should init node with passed parent'
        self.assertEqual(node.globals['some_key'], 'some value', msg=msg)

class TestIocDependencies(TestCase):
    @case('convert_to_node', parsing.convert_to_node)
    @case('parse', parsing.parse)
    @case('parsing_steps', [parsing.parse_attributes, parsing.parse_children])
    def test_dependency(self, key, expected):
        actual = ioc.CONTAINER.get(key)
        msg = 'parsing module should register default for ' + key
        self.assertEqual(actual, expected, msg=msg)

class SomeObject:
    def __init__(self, *args, **kwargs):
        pass

class TestParseObjectNode(TestCase):
    def setUp(self):
        element = ET.fromstring('<SomeObject xmlns="tests.core.parsing_test"/>')
        self.xml_node = XmlNode(element)

    def test_parse_raises(self):
        msg = 'parse should raise error if method "convert_to_node" is not registered'
        with self.assertRaises(NotImplementedError, msg=msg):
            parsing.parse(self.xml_node, parsing.NodeArgs(self.xml_node))

class TestGetModifier(TestCase):
    @case('', setattr)
    @case('attr_name', setattr)
    @case('{tests.core.parsing_test.some_modifier}', some_modifier)
    @case('{tests.core.parsing_test.some_modifier}attr_name', some_modifier)
    def test_get_modifier(self, name, expected):
        xml_attr = XmlAttr((name, ''))
        actual = parsing.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @case('{}')
    @case('{}attr_name')
    @case('{tests.core.parsing_test.some_modifier_not}attr_name')
    def test_get_modifier_raises(self, name):
        msg = 'get_modifier should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr((name, ''))
            parsing.get_modifier(xml_attr)

class TestExpressions(TestCase):
    @case('{asdf}', True)
    @case('{{asdf}}', True)
    @case('{asdf', False)
    @case('asdf}', False)
    @case(' {asdf}', False)
    def test_is_code_expression(self, expr, expected):
        self.assertEqual(parsing.is_code_expression(expr), expected)

    @case('{asdf}', 'asdf')
    @case('asdf', 'sd')
    def test_parse_code_expression(self, expr, expected):
        self.assertEqual(parsing.parse_code_expression(expr), expected)

if __name__ == '__main__':
    main()
