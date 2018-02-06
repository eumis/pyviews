from tempfile import TemporaryFile
from unittest import TestCase, main
from tests.utility import case
from pyviews.core.xml import Parser

class ParsingTests(TestCase):
    def _parse(self, xml_string):
        parser = Parser()

        with TemporaryFile() as xml_file:
            xml_file.write(xml_string.encode())
            xml_file.seek(0)
            return parser.parse(xml_file)

    def _get_child(self, root, level):
        i = 0
        node = root
        while i < level:
            node = node.children[0]
            i = i + 1
        return node

    @case('<r xmlns="nsp"/>', 'nsp')
    @case('<r xmlns="nsp" xmlns:h="h"/>', 'nsp')
    @case('<h:r xmlns="nsp" xmlns:h="h"/>', 'h')
    def test_namespace_definition(self, xml_string, namespace):
        root = self._parse(xml_string)

        msg = 'Namespace shoud be parsed correctly'
        self.assertEqual(namespace, root.namespace, msg)

    @case('<r xmlns="nsp"><c1 /></r>', 'nsp', 1)
    @case('<r xmlns="nsp" xmlns:h="h"><c1 /></r>', 'nsp', 1)
    @case('<r xmlns="nsp" xmlns:h="h"><h:c1 /></r>', 'h', 1)
    @case('<r xmlns="nsp"><c1><c2/></c1></r>', 'nsp', 2)
    @case('<r xmlns="nsp" xmlns:h="h"><c1><c2/></c1></r>', 'nsp', 2)
    @case('<r xmlns="nsp" xmlns:h="h"><c1><h:c2/></c1></r>', 'h', 2)
    def test_parent_namespace_definition(self, xml_string, namespace, child_level):
        root = self._parse(xml_string)
        child = self._get_child(root, child_level)

        msg = 'Namespace shoud be parsed correctly'
        self.assertEqual(namespace, child.namespace, msg)

    #second parameter is somethig like newick notation
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


if __name__ == '__main__':
    main()
