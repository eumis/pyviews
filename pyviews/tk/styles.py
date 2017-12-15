from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.compilation import Expression
from pyviews.core.node import Node, InheritedDict
from pyviews.core.parsing import is_code_expression, parse_expression, get_modifier
from pyviews.tk.containers import View, Container

class StyleItem:
    def __init__(self, modifier, name, value):
        self._modifier = modifier
        self._name = name
        self._value = value

    def apply(self, node):
        self._modifier(node, self._name, self._value)

class Style(Node):
    def __init__(self, xml_node, parent_context=None):
        super().__init__(xml_node, parent_context)
        self._styles = parent_context['styles']
        self.name = None

    def set_items(self, items):
        if not self.name:
            raise KeyError("style doesn't have name")
        self._styles[self.name] = items

    def destroy(self):
        self._styles.remove_key(self.name)
        self._destroy_bindings()

class Styles(View):
    def __init__(self, master, xml_node: XmlNode, parent_context=None):
        super().__init__(master, xml_node, parent_context)
        self._parent_context = parent_context
        self._name = None

    def parse_children(self):
        if self._name:
            super().parse_children()
        else:
            Container.parse_children(self)

    def get_node_args(self, xml_node: XmlNode):
        args = super().get_node_args(xml_node)
        args['parent_context'] = self._parent_context
        return args

def init_styles(node: Node):
    node.context['styles'] = InheritedDict()

def parse_attrs(node: Style):
    attrs = node.xml_node.get_attrs()
    try:
        node.name = next(attr.value for attr in attrs if attr.name == 'name')
    except StopIteration:
        raise KeyError('name attribute is required for style')
    style_items = [_get_item(node, attr) for attr in attrs if attr.name != 'name']
    node.set_items(style_items)

def _get_item(node: Style, attr: XmlAttr):
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        expression = Expression(parse_expression(value)[1])
        value = expression.execute(node.globals.to_dictionary())
    return StyleItem(modifier, attr.name, value)

def apply_styles(node, styles):
    keys = styles.split(',') if isinstance(styles, str) else styles
    styles = node.context['styles']
    for key in [key for key in keys if key]:
        for item in styles[key]:
            item.apply(node)
