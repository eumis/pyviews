from unittest import TestCase, main
from xml.etree import ElementTree as ET
from pyviews.core.xml import XmlNode
from pyviews.core.parsing import Node

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

if __name__ == '__main__':
    main()
