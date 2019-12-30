from injectool import resolve

from pyviews.binding import Binder, BindingContext
from pyviews.compilation import is_expression, parse_expression
from pyviews.core import Node, XmlAttr, import_path


def apply_attributes(node: Node, *_):
    """Rendering step: applies xml attributes to instance node and setups bindings"""
    for attr in node.xml_node.attrs:
        apply_attribute(node, attr)


def apply_attribute(node: Node, attr: XmlAttr):
    """Maps xml attribute to instance node property and setups bindings"""
    setter = get_setter(attr)
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        (binding_type, expr_body) = parse_expression(stripped_value)
        binder = resolve(Binder)
        binder.apply(binding_type, BindingContext({
            'node': node,
            'expression_body': expr_body,
            'modifier': setter,
            'xml_attr': attr
        }))
    else:
        setter(node, attr.name, attr.value)


def get_setter(attr: XmlAttr):
    """Returns modifier for xml attribute"""
    if attr.namespace is None:
        return call_set_attr
    return import_path(attr.namespace)


def call_set_attr(node: Node, key: str, value):
    """Modifier: calls node setter"""
    node.set_attr(key, value)

#
# def render_children(node: Node, child_context: RenderingContext):
#     """renders node children"""
#     for xml_node in node.xml_node.children:
#         child = render(xml_node, child_context)
#         node.add_child(child)
