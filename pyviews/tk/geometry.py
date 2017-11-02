from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.parsing import Node
from pyviews.tk.widgets import WidgetNode
from pyviews.core.parsing import parse_attributes

class Geometry:
    def __init__(self):
        self._args = {}

    def set(self, key, value):
        self._args[key] = value

    def items(self):
        return self._args.items()

    def apply(self, widget):
        pass

class GridGeometry(Geometry):
    def __init__(self, row=None, col=None, **args):
        super().__init__()
        self._args = args if args else self._args
        self.set('row', row)
        self.set('column', col)

    def apply(self, widget):
        widget.grid(**self._args)

class PackGeometry(Geometry):
    def __init__(self, **args):
        super().__init__()
        self._args = args if args else self._args

    def apply(self, widget):
        widget.pack(**self._args)

class LayoutSetup(Node):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self._master = master
        self._args = {}
        self._index = None

    def set_attr(self, key, value):
        if key == 'index':
            self._index = value
        else:
            self._args[key] = value

    def apply(self):
        pass

class Row(LayoutSetup):
    def apply(self):
        self._master.grid_rowconfigure(self._index, **self._args)

class Column(LayoutSetup):
    def apply(self):
        self._master.grid_columnconfigure(self._index, **self._args)

def apply_layout(layout: LayoutSetup):
    parse_attributes(layout)
    layout.apply()
