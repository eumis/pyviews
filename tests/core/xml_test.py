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
        tested.ET.xml = \
            '''<?xml version="1.0"?>
            <get_root_test xmlns='some.namespace' />
            '''
        root = tested.get_root('')

        self.assertIsInstance(root, tested.XmlNode, 'get_root should return XmlNode')
        self.assertEqual(root.class_name, 'get_root_test', 'get_root should return root of passed xml')

    @case('<?xml version="1.0"?><get_root_test/>')
    @case('<get_root_test>')
    @case('<get_root_test><<get_root_test/>')
    @case('<get_root_test><get_root_testtst/>')
    @case('get_root_test><get_root_test/>')
    @case('<get_root_test xmlns=namespace><get_root_test/>')
    def test_get_root_raises(self, xml):
        tested.ET.xml = xml
        with self.assertRaises(tested.ParsingError, msg='get_root should raise error for invalid xml'):
            tested.get_root('')

if __name__ == '__main__':
    main()
