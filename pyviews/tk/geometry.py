from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.parsing import Node
from pyviews.core.parsing import parse_attributes

class Geometry:
    def __init__(self, **args):
        self._args = args if args else {}

    def set(self, key, value):
        self._args[key] = value

    def apply(self, widget):
        pass

class GridGeometry(Geometry):
    def apply(self, widget):
        widget.grid(**self._args)

class PackGeometry(Geometry):
    def apply(self, widget):
        widget.pack(**self._args)

class PlaceGeometry(Geometry):
    def apply(self, widget):
        widget.place(**self._args)

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
