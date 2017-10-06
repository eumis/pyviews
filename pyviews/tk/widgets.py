from tkinter import Widget
from pyviews.core.xml import XmlNode
from pyviews.core.parsing import Node, NodeArgs

class WidgetArgs(NodeArgs):
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self.widget_master = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return []
        return super().get_args(inst_type=None)

    def get_kwargs(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return {k}
        return super().get_args(inst_type=None)

class WidgetNode(Node):
    def __init__(self, widget, xml_node: XmlNode, parent: Node = None):
        super().__init__(xml_node, parent)
        self.widget = widget
