from unittest import TestCase, main
from xml.etree import ElementTree as ET
from tests.utility import case
from pyviews.core import xml

class ParsingTests(TestCase):
    @case('{namespace}name', ('namespace', 'name'))
    @case('{namespace}{name}', ('namespace', '{name}'))
    @case('{namespace}n}ame', ('namespace', 'n}ame'))
    @case('{namespace}', ('namespace', ''))
    def test_parse_namespace(self, expression, expected):
        self.assertEqual(xml.parse_namespace(expression), expected)

    @case('namespace.name')
    @case('namespace}.name')
    @case('namespace{name}')
    def test_parse_namespace_rases(self, expression):
        with self.assertRaises(xml.ParsingError):
            xml.parse_namespace(expression)

    @case('namespace.name', False)
    @case('namespace}.name', False)
    @case('{namespace.name', False)
    @case('namespace{name}', False)
    @case('namespace{name}', False)
    @case('{namespacename}', True)
    @case('{namespace}name', True)
    @case('{namespace}{name}', True)
    def test_has_namespace(self, expression, has):
        self.assertEqual(xml.has_namespace(expression), has)

class ETMock:
    def __init__(self):
        self.xml = None
        self.ParseError = ET.ParseError

    def parse(self, path):
        return ET.ElementTree(ET.fromstring(self.xml))

class TestGetRoot(TestCase):
    def setUp(self):
        xml.__dict__['ET'] = ETMock()

    def tearDown(self):
        xml.__dict__['ET'] = ET

    def test_get_root(self):
        xml.ET.xml = '<?xml version="1.0"?><someroot xmlns="some.namespace" />'
        root = xml.get_root('')

        self.assertIsInstance(root, xml.XmlNode, 'get_root should return XmlNode')
        self.assertEqual(root.class_name, 'someroot', 'get_root should return root of passed xml')

    @case('<?xml version="1.0"?><someroot/>')
    @case('<someroot>')
    @case('<someroot><<someroot/>')
    @case('<someroot><someroottst/>')
    @case('someroot><someroot/>')
    @case('<someroot xmlns=namespace><someroot/>')
    def test_get_root_raises(self, xml_string):
        xml.ET.xml = xml_string
        msg = 'get_root should raise error for invalid xml'
        with self.assertRaises(xml.ParsingError, msg=msg):
            xml.get_root('')

class TestXmlNode(TestCase):
    def test_constructor(self):
        element = ET.fromstring('<someroot xmlns="some.namespace" />')
        node = xml.XmlNode(element)

        msg = 'XmlNode should use namespace as module'
        self.assertEqual(node.module_name, 'some.namespace', msg)
        self.assertEqual(node.class_name, 'someroot', msg)

    def test_get_children(self):
        element = ET.fromstring(
            '''<someroot xmlns="some.namespace"
                            xmlns:ch='some.child.namespace'>
                <ch:child></ch:child>
                <ch:child></ch:child>
            </someroot>''')
        node = xml.XmlNode(element)
        children = node.get_children()

        self.assertEqual(len(children), 2, 'XmlNode.get_children should return children''s count')
        for child in children:
            msg = 'child should be XmlNode'
            self.assertIsInstance(child, xml.XmlNode, msg)

            msg = 'Child XmlNode should use namespace as module'
            self.assertEqual(child.module_name, 'some.child.namespace', msg)
            self.assertEqual(child.class_name, 'child', msg)

    def test_get_attrs(self):
        element = ET.fromstring(
            '''<someroot xmlns='some.namespace'
                            xmlns:ch='some.child.namespace'
                        one='value'
                        ch:two='namespace value'>
            </someroot>''')
        node = xml.XmlNode(element)
        attrs = node.get_attrs()

        self.assertEqual(len(attrs), 2, 'XmlNode.get_children should return attrribute''s count')
        for attr in attrs:
            self.assertIsInstance(attr, xml.XmlAttr, 'child should be XmlNode')

        self.assertEqual(attrs[0].name, 'one', 'XmlNode should return correct attribute name')
        self.assertEqual(attrs[0].value, 'value', 'XmlNode should return correct attribute value')
        self.assertEqual(attrs[0].namespace, None, 'XmlNode should return correct namespace')

        self.assertEqual(attrs[1].name, 'two', 'XmlNode should return correct attribute name')
        self.assertEqual(attrs[1].value, 'namespace value', 'XmlNode should return correct attribute value')
        self.assertEqual(attrs[1].namespace, 'some.child.namespace', 'XmlNode should return correct namespace')

class TestXmlAttr(TestCase):
    @case(('one', 'two'), None, 'one', 'two')
    @case(('{some.namespace}one', 'two'), 'some.namespace', 'one', 'two')
    def test_constructor(self, attr, namespace, name, value):
        attr = xml.XmlAttr(attr)

        self.assertEqual(attr.namespace, namespace, 'XmlAttr should use namespace')
        self.assertEqual(attr.name, name, 'XmlAttr should use name')
        self.assertEqual(attr.value, value, 'XmlAttr should use value')

if __name__ == '__main__':
    main()
