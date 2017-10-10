from tkinter import Tk, Widget
from collections import namedtuple
from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.parsing import Node, NodeArgs
from pyviews.tk.views import get_view_root

class WidgetArgs(NodeArgs):
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self['master'] = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return namedtuple('Args', ['args', 'kwargs'])([self['master']], {})
        return super().get_args(inst_type)

class WidgetNode(Node):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
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
    def __init__(self, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(Tk(), xml_node, parent_globals)

    @property
    def state(self):
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)

class Container(Node):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self.master = master

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def set_attr(self, key, value):
        setattr(self, key, value)

    def get_node_args(self, xml_node):
        return WidgetArgs(xml_node, self, self.master)

class View(Container):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(master, xml_node, parent_globals)
        self.name = None

    @inject('parse')
    def parse_children(self, parse=None):
        self.destroy_children()
        root_xml = get_view_root(self.name)
        self._child_nodes = [parse(root_xml, self.get_node_args(root_xml))]
