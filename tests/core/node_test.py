from unittest import TestCase, main
from xml.etree import ElementTree as ET
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node, NodeArgs

class TestNodeArgs(TestCase):
    def test_node_args(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = Node(xml_node)
        args = NodeArgs(xml_node, node).get_args(Node)

        msg = 'NodeArgs should return XmlNode as args'
        self.assertEqual([xml_node], args.args, msg)

        msg = 'NodeArgs should return parent as kargs'
        self.assertEqual({'parent_context': node.context}, args.kwargs, msg)

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

if __name__ == '__main__':
    main()
