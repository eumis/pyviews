# pylint: disable=missing-docstring

from tempfile import TemporaryFile
from unittest import TestCase
from .ioc import Scope, register_single
from pyviews.testing import case
from .xml import Parser, XmlAttr, XmlError


class ParsingTests(TestCase):
    @staticmethod
    def _parse(xml_string, namespaces: dict = None):
        if namespaces is None:
            namespaces = {}

        with Scope('ParsingTests'):
            register_single('namespaces', namespaces)
            with TemporaryFile() as xml_file:
                xml_file.write(xml_string.encode())
                xml_file.seek(0)
                return Parser().parse(xml_file)

    @staticmethod
    def _get_child(root, level):
        i = 0
        node = root
        while i < level:
            node = node.children[0]
            i = i + 1
        return node

    @case({'': 'nsp'}, '<r />', 'nsp')
    @case({'': 'nsp'}, '<r />', 'nsp')
    @case({'': 'nsp', 'h': 'h'}, '<r />', 'nsp')
    @case({'': 'nsp', 'h': 'h'}, '<h:r />', 'h')
    @case({'': 'default'}, '<r xmlns="nsp"/>', 'nsp')
    @case({'': 'default'}, '<r xmlns="nsp" xmlns:h="h"/>', 'nsp')
    @case({'h': 'default'}, '<h:r xmlns="nsp" xmlns:h="h"/>', 'h')
    def test_namespace_definition(self, namespaces, xml_string, expected):
        root = self._parse(xml_string, namespaces)

        msg = 'Namespace should be parsed correctly'
        self.assertEqual(expected, root.namespace, msg)

    @case({}, '<r xmlns="nsp"><c1 /></r>', 'nsp', 1)
    @case({'': 'nsp'}, '<r xmlns="nsp"><c1 /></r>', 'nsp', 1)
    @case({}, '<r xmlns="nsp" xmlns:h="h"><c1 /></r>', 'nsp', 1)
    @case({'': 'nsp'}, '<r xmlns:h="h"><c1 /></r>', 'nsp', 1)
    @case({}, '<r xmlns="nsp" xmlns:h="h"><h:c1 /></r>', 'h', 1)
    @case({'h': 'h'}, '<r xmlns="nsp"><h:c1 /></r>', 'h', 1)
    @case({}, '<r xmlns="nsp"><c1><c2/></c1></r>', 'nsp', 2)
    @case({}, '<r xmlns="nsp" xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2)
    @case({'': 'nsp'}, '<r xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2)
    @case({}, '<r xmlns="nsp" xmlns:h="h"><c1><h:c2/></c1></r>', 'h', 2)
    @case({'h': 'h'}, '<r xmlns="nsp"><c1><h:c2/></c1></r>', 'h', 2)
    def test_parent_namespace_definition(self, namespaces, xml_string, expected, child_level):
        root = self._parse(xml_string, namespaces)
        child = self._get_child(root, child_level)

        msg = 'Namespace should be parsed correctly'
        self.assertEqual(expected, child.namespace, msg)

    @case("<r xmlns='n'><c1/></r>", [0])
    @case("<r xmlns='n'><c1/><c1/><c1/></r>", [0, 0, 0])
    @case("<r xmlns='n'><c1/><c1><c2/><c2/></c1><c1><c2/></c1></r>", [0, [0, 0], [0]])
    def test_nodes_structure(self, xml_string, structure):
        root = self._parse(xml_string)

        self._assert_right_children(root, structure)

    def _assert_right_children(self, root, structure):
        msg = 'Parser should add child to parent'
        self.assertEqual(len(root.children), len(structure), msg)
        for i, child_structure in enumerate(structure):
            child = root.children[i]
            if child_structure == 0:
                self.assertEqual(len(child.children), 0, msg)
            else:
                self._assert_right_children(child, child_structure)

    @case({},
          "<r xmlns='n' xmlns:m='nsp' k='{1}' m:k='v' m:a='value'/>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          0)
    @case({'': 'n', 'm': 'nsp'},
          "<r k='{1}' m:k='v' m:a='value'/>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          0)
    @case({},
          "<r xmlns='n' xmlns:m='nsp'><c1 k='{1}' m:k='v' m:a='value'/></r>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          1)
    @case({'': 'n', 'm': 'nsp'},
          "<r><c1 k='{1}' m:k='v' m:a='value'/></r>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          1)
    @case({},
          "<r xmlns='n' xmlns:m='nsp'><c1><c2 k='{1}' m:k='v' m:a='value'/></c1></r>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          2)
    @case({'': 'n', 'm': 'nsp'},
          "<r><c1><c2 k='{1}' m:k='v' m:a='value'/></c1></r>",
          [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
          2)
    def test_attribute_parsing(self, namespaces, xml_string, expected, level):
        root = self._parse(xml_string, namespaces)
        parsed_attrs = self._get_child(root, level).attrs

        msg = 'attributes should be parsed correctly'
        self.assertEqual(len(parsed_attrs), len(expected), msg)
        self._assert_attributes_equal(expected, parsed_attrs, msg)

    def _assert_attributes_equal(self, expected, parsed_attrs, msg):
        for i, parsed_attr in enumerate(parsed_attrs):
            attr = expected[i]
            self.assertEqual(attr.name, parsed_attr.name, msg)
            self.assertEqual(attr.value, parsed_attr.value, msg)
            self.assertEqual(attr.namespace, parsed_attr.namespace, msg)

    @case("<r />")
    @case("<nsp:r xmlns='n' />")
    @case('''
            <r xmlns='n'>
                <c1>
                    <c2>

                    <c2></c2>
                </c1>
            </r>
          ''')
    @case('''
            <r xmlns='n'>
                <c1>
                    <c2 a='></c2>
                </c1>
            </r>
          ''')
    def test_raises_for_bad_xml(self, xml_string):
        with self.assertRaises(XmlError):
            self._parse(xml_string)
