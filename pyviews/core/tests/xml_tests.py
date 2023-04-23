from tempfile import TemporaryFile

from pytest import mark, raises

from pyviews.core.xml import XmlAttr, XmlError, XmlNode, parse


def _parse(xml_string):
    with TemporaryFile() as xml_file:
        xml_file.write(xml_string.encode())
        xml_file.seek(0)
        return parse(xml_file)


def _get_child(root: XmlNode, level: int):
    i = 0
    node = root
    while i < level:
        node = node.children[0]
        i = i + 1
    return node


class ParsingTests:

    @staticmethod
    @mark.parametrize('xml_string, expected', [
        ('<r xmlns="nsp"/>', 'nsp'),
        ('<r xmlns="nsp" xmlns:h="h"/>', 'nsp'),
        ('<h:r xmlns="nsp" xmlns:h="h"/>', 'h')
    ]) # yapf: disable
    def test_namespace_definition(xml_string, expected):
        """namespaces should be parsed"""
        root = _parse(xml_string)

        assert expected == root.namespace

    @staticmethod
    @mark.parametrize('xml_string, expected, child_level', [
        ('<r xmlns="nsp"><c1 /></r>', 'nsp', 1),
        ('<r xmlns="nsp" xmlns:h="h"><c1 /></r>', 'nsp', 1),
        ('<r xmlns="nsp" xmlns:h="h"><h:c1 /></r>', 'h', 1),
        ('<r xmlns="nsp" xmlns:h="h"><c1 /></r>', 'nsp', 1),
        ('<r xmlns="nsp"><c1><c2/></c1></r>', 'nsp', 2),
        ('<r xmlns="nsp" xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2),
        ('<r xmlns="nsp" xmlns:h="h"><c1><h:c2/></c1></r>', 'h', 2)
    ]) # yapf: disable
    def test_parent_namespace_definition(xml_string, expected, child_level):
        """child namespaces should be parsed"""
        root = _parse(xml_string)
        child = _get_child(root, child_level)

        assert expected == child.namespace

    @mark.parametrize('xml_string, structure', [
        ("<r xmlns='n'><c1/></r>", [0]),
        ("<r xmlns='n'><c1/><c1/><c1/></r>", [0, 0, 0]),
        ("<r xmlns='n'><c1/><c1><c2/><c2/></c1><c1><c2/></c1></r>", [0, [0, 0], [0]])
    ]) # yapf: disable
    def test_nodes_structure(self, xml_string, structure):
        """should return right nodes tree"""
        root = _parse(xml_string)

        self._assert_right_children(root, structure)

    def _assert_right_children(self, root, structure):
        assert len(root.children) == len(structure)
        for i, child_structure in enumerate(structure):
            child = root.children[i]
            if child_structure == 0:
                assert not child.children
            else:
                self._assert_right_children(child, child_structure)

    @staticmethod
    @mark.parametrize('xml_string, expected, level', [
        ("<r xmlns='n' xmlns:m='nsp' k='{1}' m:k='v' m:a='value'/>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         0),
        ("<r xmlns='n' xmlns:m='nsp'><c1 k='{1}' m:k='v' m:a='value'/></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         1),
        ("<r xmlns='n' xmlns:m='nsp'><c1><c2 k='{1}' m:k='v' m:a='value'/></c1></r>",
         [XmlAttr('k', '{1}'), XmlAttr('k', 'v', 'nsp'), XmlAttr('a', 'value', 'nsp')],
         2)
    ]) # yapf: disable
    def test_attribute_parsing(xml_string, expected, level):
        """should parse attributes"""
        root = _parse(xml_string)
        parsed_attrs = _get_child(root, level).attrs

        assert len(parsed_attrs) == len(expected)
        for i, parsed_attr in enumerate(parsed_attrs):
            attr = expected[i]
            assert attr.name == parsed_attr.name
            assert attr.value == parsed_attr.value
            assert attr.namespace == parsed_attr.namespace

    @staticmethod
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
    ]) # yapf: disable
    def test_raises_for_bad_xml(xml_string):
        """should raise XmlError for bad formed xml"""
        with raises(XmlError):
            _parse(xml_string)
