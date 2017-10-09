from tkinter import Tk, Widget
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
            return {'parent': self.widget_master}
        return super().get_args(inst_type=None)

class WidgetNode(Node):
    def __init__(self, widget, xml_node: XmlNode, parent: Node = None):
        super().__init__(xml_node, parent)
        self.widget = widget

    def get_node_args(self, xml_node: XmlNode):
        return WidgetArgs(xml_node, self, self.widget)

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def bind(self, event, command):
        self.widget.bind('<'+event+'>', command)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            super().__setattr__(key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

class Root(WidgetNode):
    def __init__(self, xml_node: XmlNode, parent: Node = None):
        super().__init__(Tk(), xml_node, parent)

    @property
    def state(self):
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)
