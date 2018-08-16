from unittest import TestCase, main
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node, RenderArgs

class NodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('namespace', 'root')
        self.node = Node(self.xml_node)

    def test_init_xml_node(self):
        node = Node(self.xml_node)

        msg = 'Node should inititalise properties'
        self.assertEqual(node.xml_node, self.xml_node, msg)

    def test_init_setup_globals(self):
        node = Node(self.xml_node)

        msg = 'init should setup globals'
        self.assertIsNotNone(node.globals)

        msg = 'init should add node to globals'
        self.assertEqual(node, node.globals['node'], msg)

if __name__ == '__main__':
    main()
