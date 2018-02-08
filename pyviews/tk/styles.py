from pyviews.core.xml import XmlAttr
from pyviews.core.ioc import inject
from pyviews.core.compilation import Expression
from pyviews.core.node import Node
from pyviews.core.parsing import is_code_expression, parse_expression, get_modifier

class StyleItem:
    def __init__(self, modifier, name, value):
        self._modifier = modifier
        self._name = name
        self._value = value

    def apply(self, node):
        self._modifier(node, self._name, self._value)

class Style(Node):
    def __init__(self, xml_node, parent_context=None, parent_style=None):
        super().__init__(xml_node, parent_context)
        self._parent_style = parent_style
        self.name = None

    @inject('styles')
    def set_items(self, items, styles=None):
        if not self.name:
            raise KeyError("style doesn't have name")
        if self._parent_style:
            parent_items = [pi for pi in styles[self._parent_style] \
                if all(i._name != pi._name or i._modifier != pi._modifier for i in items)]
            items = parent_items + items
        styles[self.name] = items

    def get_node_args(self, xml_node):
        args = super().get_node_args(xml_node)
        args['parent_style'] = self.name
        return args

    @inject('styles')
    def destroy(self, styles=None):
        del styles[self.name]
        self._destroy_bindings()

def parse_attrs(node: Style):
    attrs = node.xml_node.attrs
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

@inject('styles')
def apply_styles(node, style_keys, styles=None):
    keys = [key.strip() for key in style_keys.split(',')] \
            if isinstance(style_keys, str) else style_keys
    for key in [key for key in keys if key]:
        for item in styles[key]:
            item.apply(node)
