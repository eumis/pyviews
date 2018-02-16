from unittest import TestCase, main
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node, NodeArgs

class NodeArgsTests(TestCase):
    def test_get_args(self):
        xml_node = XmlNode('namespace', 'root')
        node = Node(xml_node)
        args = NodeArgs(xml_node, node).get_args(Node)

        msg = 'NodeArgs should return XmlNode as args'
        self.assertEqual([xml_node], args.args, msg)

        msg = 'NodeArgs should return parent as kargs'
        self.assertEqual({'parent_context': node.context}, args.kwargs, msg)

class NodeTests(TestCase):
    def test_init(self):
        xml_node = XmlNode('namespace', 'root')
        node = Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

if __name__ == '__main__':
    main()
