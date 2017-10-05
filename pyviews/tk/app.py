from pyviews.core.xml import XmlNode
from pyviews.core.parsing import Node

class WidgetNode(Node):
    def __init__(self, xml_node: XmlNode, parent: Node = None):
        super().__init__(xml_node, parent)
