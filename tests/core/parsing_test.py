from unittest import TestCase, main
from xml.etree import ElementTree as ET
from tests.utility import case
from tests.mock import some_modifier
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core import parsing

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = parsing.Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

class TestMethods(TestCase):
    @case('', setattr)
    @case('attr_name', setattr)
    @case('{tests.core.parsing_test.some_modifier}', some_modifier)
    @case('{tests.core.parsing_test.some_modifier}attr_name', some_modifier)
    def test_get_modifier(self, name, expected):
        xml_attr = XmlAttr((name, ''))
        actual = parsing.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @case('{}', setattr)
    @case('{}attr_name', setattr)
    @case('{tests.core.parsing_test.some_modifier_not}attr_name', some_modifier)
    def test_get_modifier_raises(self, name, exptected):
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
    def test_parse_one_way_binding(self, expr, expected):
        self.assertEqual(parsing.parse_code_expression(expr), expected)

if __name__ == '__main__':
    main()
