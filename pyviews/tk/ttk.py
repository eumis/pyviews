from tkinter.ttk import Style as TtkStyle
from pyviews.core.node import Node
from pyviews.tk.widgets import WidgetNode

class TtkWidgetNode(WidgetNode):
    @property
    def style(self):
        return self.widget.cget('style')

    @style.setter
    def style(self, value):
        self.widget.config(style=value)

class Style(Node):
    def __init__(self, xml_node, parent_context=None, parent_name=None):
        super().__init__(xml_node, parent_context)
        self.values = {}
        self._parent_name = parent_name
        self.name = None

    @property
    def full_name(self):
        return '{0}.{1}'.format(self.name, self._parent_name) \
               if self._parent_name else self.name

    def set_attr(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.values[key] = value

    def apply(self):
        ttk_style = TtkStyle()
        if not self.name:
            raise KeyError("style doesn't have name")
        ttk_style.configure(self.full_name, **self.values)

    def get_node_args(self, xml_node):
        args = super().get_node_args(xml_node)
        args['parent_name'] = self.full_name
        return args

def theme_use(node, key, value):
    ttk_style = TtkStyle()
    ttk_style.theme_use(key)

def apply_ttk_style(node):
    node.apply()
