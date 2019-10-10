from tempfile import TemporaryFile

from injectool import make_default, add_singleton
from pytest import mark, raises

from pyviews.core.xml import Parser, XmlAttr, XmlError, XmlNode


class ParsingTests:
    @staticmethod
    def _parse(xml_string, namespaces: dict = None):
        if namespaces is None:
            namespaces = {}

        with make_default('ParsingTests'):
            add_singleton('namespaces', namespaces)
            with TemporaryFile() as xml_file:
                xml_file.write(xml_string.encode())
                xml_file.seek(0)
                return Parser().parse(xml_file)

    @staticmethod
    def _get_child(root: XmlNode, level):
        i = 0
        node = root
        while i < level:
            node = node.children[0]
            i = i + 1
        return node

    @mark.parametrize('namespaces, xml_string, expected', [
        ({'': 'nsp'}, '<r />', 'nsp'),
        ({'': 'nsp'}, '<r />', 'nsp'),
        ({'': 'nsp', 'h': 'h'}, '<r />', 'nsp'),
        ({'': 'nsp', 'h': 'h'}, '<h:r />', 'h'),
        ({'': 'default'}, '<r xmlns="nsp"/>', 'nsp'),
        ({'': 'default'}, '<r xmlns="nsp" xmlns:h="h"/>', 'nsp'),
        ({'h': 'default'}, '<h:r xmlns="nsp" xmlns:h="h"/>', 'h')
    ])
    def test_namespace_definition(self, namespaces, xml_string, expected):
        """namespaces should be parsed"""
        root = self._parse(xml_string, namespaces)

        assert expected == root.namespace

    @mark.parametrize('namespaces, xml_string, expected, child_level', [
        ({}, '<r xmlns="nsp"><c1 /></r>', 'nsp', 1),
        ({'': 'nsp'}, '<r xmlns="nsp"><c1 /></r>', 'nsp', 1),
        ({}, '<r xmlns="nsp" xmlns:h="h"><c1 /></r>', 'nsp', 1),
        ({'': 'nsp'}, '<r xmlns:h="h"><c1 /></r>', 'nsp', 1),
        ({}, '<r xmlns="nsp" xmlns:h="h"><h:c1 /></r>', 'h', 1),
        ({'h': 'h'}, '<r xmlns="nsp"><h:c1 /></r>', 'h', 1),
        ({}, '<r xmlns="nsp"><c1><c2/></c1></r>', 'nsp', 2),
        ({}, '<r xmlns="nsp" xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2),
        ({'': 'nsp'}, '<r xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2),
        ({}, '<r xmlns="nsp" xmlns:h="h"><c1><h:c2/></c1></r>', 'h', 2),
        ({'h': 'h'}, '<r xmlns="nsp"><c1><h:c2/></c1></r>', 'h', 2)
    ])
    def test_parent_namespace_definition(self, namespaces, xml_string, expected, child_level):
        """child namespaces should be parsed"""
        root = self._parse(xml_string, namespaces)
        child = self._get_child(root, child_level)

        assert expected == child.namespace

    @mark.parametrize('xml_string, structure', [
        ("<r xmlns='n'><c1/></r>", [0]),
        ("<r xmlns='n'><c1/><c1/><c1/></r>", [0, 0, 0]),
        ("<r xmlns='n'><c1/><c1><c2/><c2/></c1><c1><c2/></c1></r>", [0, [0, 0], [0]])
    ])
    def test_nodes_structure(self, xml_string, structure):
        """should return right nodes tree"""
        root = self._parse(xml_string)

        self._assert_right_children(root, structure)

    def _assert_right_children(self, root, structure):
        assert len(root.children) == len(structure)
        for i, child_structure in enumerate(structure):
            child = root.children[i]
            if child_structure == 0:
                assert not child.children
            else:
                self._assert_right_children(child, child_structure)

    @mark.parametrize('namespaces, xml_string, expected, level', [
        ({},
         "<r xmlns='n' xmlns:m='nsp' k='{1}' m:k='v' m:a='value'/>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         0),
        ({'': 'n', 'm': 'nsp'},
         "<r k='{1}' m:k='v' m:a='value'/>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         0),
        ({},
         "<r xmlns='n' xmlns:m='nsp'><c1 k='{1}' m:k='v' m:a='value'/></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         1),
        ({'': 'n', 'm': 'nsp'},
         "<r><c1 k='{1}' m:k='v' m:a='value'/></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         1),
        ({},
         "<r xmlns='n' xmlns:m='nsp'><c1><c2 k='{1}' m:k='v' m:a='value'/></c1></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         2),
        ({'': 'n', 'm': 'nsp'},
         "<r><c1><c2 k='{1}' m:k='v' m:a='value'/></c1></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         2)
    ])
    def test_attribute_parsing(self, namespaces, xml_string, expected, level):
        """should parse attributes"""
        root = self._parse(xml_string, namespaces)
        parsed_attrs = self._get_child(root, level).attrs

        assert len(parsed_attrs) == len(expected)
        for i, parsed_attr in enumerate(parsed_attrs):
            attr = expected[i]
            assert attr.name == parsed_attr.name
            assert attr.value == parsed_attr.value
            assert attr.namespace == parsed_attr.namespace

    @mark.parametrize('xml_string', [
        "<r />",
        "<nsp:r xmlns='n' />",
        '''
            <r xmlns='n'>
                <c1>
                    <c2>

                    <c2></c2>
                </c1>
            </r>
          ''',
        '''
            <r xmlns='n'>
                <c1>
                    <c2 a='></c2>
                </c1>
            </r>
          '''
    ])
    def test_raises_for_bad_xml(self, xml_string):
        """should raise XmlError for bad formed xml"""
        with raises(XmlError):
            self._parse(xml_string)
