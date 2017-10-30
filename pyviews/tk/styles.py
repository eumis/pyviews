from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.compilation import Expression
from pyviews.core.parsing import Node, ExpressionVars, get_modifier
from pyviews.core.parsing import is_code_expression, parse_code_expression
from pyviews.tk.widgets import View, Container

class StyleItem:
    def __init__(self, modifier, name, value):
        self._modifier = modifier
        self._name = name
        self._value = value

    def apply(self, node):
        self._modifier(node, self._name, self._value)

class Style(Node):
    def __init__(self, xml_node, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self._parent_globals = parent_globals
        self.name = None

    def apply(self, items):
        if not self.name:
            raise KeyError("style doesn't have name")
        self._parent_globals[self.name] = items

    def destroy(self):
        self._parent_globals.remove_key(self.name)
        self._destroy_bindings()

def parse_attributes(node: Style):
    attrs = node.xml_node.get_attrs()
    node.name = next(attr.value for attr in attrs if attr.name == 'name')
    style_items = [get_item(node, attr) for attr in attrs if attr.name != 'name']
    node.apply(style_items)

def get_item(node: Style, attr: XmlAttr):
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        expression = Expression(parse_code_expression(value))
        value = expression.execute(node.globals.to_all_dictionary())
    return StyleItem(modifier, attr.name, value)

class Styles(View):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(master, xml_node, parent_globals)
        self._parent_globals = parent_globals
        self._name = None

    def parse_children(self):
        if self._name:
            super().parse_children()
        else:
            Container.parse_children(self)

    def get_node_args(self, xml_node: XmlNode):
        args = super().get_node_args(xml_node)
        args['parent_globals'] = self._parent_globals
        return args
