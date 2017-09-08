from unittest import TestCase, main
from xml.etree import ElementTree as ET
from tests.utility import case
from pyviews.core import xml as tested

class TestParsing(TestCase):
    @case('{namespace}name', ('namespace', 'name'))
    @case('{namespace}{name}', ('namespace', '{name}'))
    @case('{namespace}n}ame', ('namespace', 'n}ame'))
    @case('{namespace}', ('namespace', ''))
    def test_parse_namespace(self, expression, expected):
        self.assertEqual(tested.parse_namespace(expression), expected)

    @case('namespace.name')
    @case('namespace}.name')
    @case('namespace{name}')
    def test_parse_namespace_rases(self, expression):
        with self.assertRaises(tested.ParsingError):
            tested.parse_namespace(expression)

    @case('namespace.name', False)
    @case('namespace}.name', False)
    @case('{namespace.name', False)
    @case('namespace{name}', False)
    @case('namespace{name}', False)
    @case('{namespacename}', True)
    @case('{namespace}name', True)
    @case('{namespace}{name}', True)
    def test_has_namespace(self, expression, has):
        self.assertEqual(tested.has_namespace(expression), has)

class ETMock:
    def __init__(self):
        self.xml = None
        self.ParseError = ET.ParseError

    def parse(self, path):
        return ET.ElementTree(ET.fromstring(self.xml))

class TestGetRoot(TestCase):
    def setUp(self):
        tested.__dict__['ET'] = ETMock()

    def tearDown(self):
        tested.__dict__['ET'] = ET

    def test_get_root(self):
        tested.ET.xml = '<?xml version="1.0"?><someroot xmlns="some.namespace" />'
        root = tested.get_root('')

        self.assertIsInstance(root, tested.XmlNode, 'get_root should return XmlNode')
        self.assertEqual(root.class_name, 'someroot', 'get_root should return root of passed xml')

    @case('<?xml version="1.0"?><someroot/>')
    @case('<someroot>')
    @case('<someroot><<someroot/>')
    @case('<someroot><someroottst/>')
    @case('someroot><someroot/>')
    @case('<someroot xmlns=namespace><someroot/>')
    def test_get_root_raises(self, xml):
        tested.ET.xml = xml
        with self.assertRaises(tested.ParsingError, msg='get_root should raise error for invalid xml'):
            tested.get_root('')

class TestXmlNode(TestCase):
    def test_constructor(self):
        element = ET.fromstring('<someroot xmlns="some.namespace" />')
        node = tested.XmlNode(element)

        self.assertEqual(node.module_name, 'some.namespace', 'XmlNode should use namespace as module')
        self.assertEqual(node.class_name, 'someroot', 'XmlNode should use namespace as module')

    def test_get_children(self):
        element = ET.fromstring(
            '''<someroot xmlns="some.namespace"
                            xmlns:ch='some.child.namespace'>
                <ch:child></ch:child>
                <ch:child></ch:child>
            </someroot>''')
        node = tested.XmlNode(element)
        children = node.get_children()

        self.assertEqual(len(children), 2, 'XmlNode.get_children should return children''s count')
        for child in children:
            self.assertIsInstance(child, tested.XmlNode, 'child should be XmlNode')
            self.assertEqual(child.module_name, 'some.child.namespace', 'Child XmlNode should use namespace as module')
            self.assertEqual(child.class_name, 'child', 'Child XmlNode should use namespace as module')

    def test_get_attrs(self):
        element = ET.fromstring(
            '''<someroot xmlns='some.namespace'
                            xmlns:ch='some.child.namespace'
                        one='value'
                        ch:two='namespace value'>
            </someroot>''')
        node = tested.XmlNode(element)
        attrs = node.get_attrs()

        self.assertEqual(len(attrs), 2, 'XmlNode.get_children should return attrribute''s count')
        for attr in attrs:
            self.assertIsInstance(attr, tested.XmlAttr, 'child should be XmlNode')

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
        attr = tested.XmlAttr(attr)

        self.assertEqual(attr.namespace, namespace, 'XmlAttr should use namespace')
        self.assertEqual(attr.name, name, 'XmlAttr should use name')
        self.assertEqual(attr.value, value, 'XmlAttr should use value')

if __name__ == '__main__':
    main()
