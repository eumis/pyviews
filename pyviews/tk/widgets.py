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
            return {'master': self.widget_master}
        return super().get_args(inst_type=None)

class WidgetNode(Node):
    def __init__(self, widget, xml_node: XmlNode, parent: Node = None):
        super().__init__(xml_node, parent)
        self.widget = widget
        self.geometry = None

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def get_node_args(self, xml_node: XmlNode):
        return WidgetArgs(xml_node, self, self.widget)

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def bind(self, event, command):
        self.widget.bind('<'+event+'>', command)

    def set_attr(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

class Root(WidgetNode):
    def __init__(self, xml_node: XmlNode, parent_node: Node = None):
        super().__init__(Tk(), xml_node, parent_node)

    @property
    def state(self):
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)
