"""Common rendering pipes"""

from typing import Callable, Union, Any

from injectool import resolve

from pyviews.binding import Binder, BindingContext
from pyviews.core import Node, XmlAttr, import_path, XmlNode, Setter
from pyviews.expression import is_expression, parse_expression
from pyviews.rendering import RenderingContext, render


def apply_attributes(node: Node, _: RenderingContext):
    """Rendering pipe: applies xml attributes to instance node and setups bindings"""
    for attr in node.xml_node.attrs:
        apply_attribute(node, attr)


def apply_attribute(node: Node, attr: XmlAttr, setter: Setter = None):
    """Maps xml attribute to instance node property and setups bindings"""
    setter = get_setter(attr) if setter is None else setter
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        (binding_type, expr_body) = parse_expression(stripped_value)
        binder = resolve(Binder)
        binder.bind(binding_type, BindingContext({
            'node': node,
            'expression_body': expr_body,
            'setter': setter,
            'xml_attr': attr
        }))
    else:
        setter(node, attr.name, attr.value)


def get_setter(attr: XmlAttr) -> Setter:
    """Returns setter for xml attribute"""
    if attr.namespace is None:
        return call_set_attr
    return import_path(attr.namespace)


def call_set_attr(node: Node, key: str, value):
    """Setter: calls node setter"""
    node.set_attr(key, value)


NodeType = Union[Node, Any]
RenderingContextType = Union[RenderingContext, Any]
GetChildContextType = Callable[[XmlNode, NodeType, RenderingContextType], RenderingContext]


def render_children(node: Node, context: RenderingContext,
                    get_child_context: GetChildContextType):
    """renders node children"""
    for xml_node in node.xml_node.children:
        child_node = render(get_child_context(xml_node, node, context))
        node.add_child(child_node)
