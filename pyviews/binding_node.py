from typing import Any, List, NamedTuple, Optional, Union

from pyviews.binding.expression import ExpressionBinding
from pyviews.core.binding import Binding
from pyviews.core.expression import Expression, execute, is_expression, parse_expression
from pyviews.core.rendering import Node, NodeGlobals, RenderingContext, Setter
from pyviews.core.xml import XmlNode
from pyviews.pipes import get_setter
from pyviews.rendering.pipeline import RenderingPipeline


class BindingProperty(NamedTuple):
    name: str
    setter: Setter
    value: Union[Expression, Any]


class BindingNode(Node):

    def __init__(self, xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None):
        super().__init__(xml_node, node_globals = node_globals)
        self.properties: List[BindingProperty] = []
        self.target: Any = None
        self.when_changed: Optional[Expression] = None
        self.when_true: Optional[Expression] = None
        self.execute_on_bind: bool = True
        self.binding: Optional[Binding] = None

    def destroy(self):
        if self.binding is not None:
            self.binding.destroy()
            self.binding = None


def get_binding_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(
        pipes = [apply_attributes, set_target, bind_changed, bind_true],
        name = 'container pipeline',
        create_node = create_binding_node
    )


def apply_attributes(node: BindingNode, _: RenderingContext):
    """Rendering pipe: records attributes to bind"""
    for attr in node.xml_node.attrs:
        value = attr.value.strip() if attr.value else ''
        if is_expression(value):
            value = Expression(parse_expression(value)[1])
        if attr.name == 'when_changed':
            node.when_changed = value
        elif attr.name == 'when_true':
            node.when_true = value
        elif attr.name in node.__dict__:
            setattr(node, attr.name, execute(value, node.node_globals))
        else:
            setter = get_setter(attr)
            node.properties.append(BindingProperty(attr.name, setter, value))


def set_target(node: BindingNode, context: RenderingContext):
    """Rendering pipe: sets target"""
    if node.target is None:
        node.target = context.parent_node


def bind_changed(node: BindingNode, _: RenderingContext):
    """Rendering pipe: creates binding"""
    if node.when_changed:
        binding = ExpressionBinding(lambda _: binding_callback(node), node.when_changed, node.node_globals)
        binding.bind(node.execute_on_bind)
        node.binding = binding


def binding_callback(node: BindingNode):
    for prop in node.properties:
        value = execute(prop.value, node.node_globals) \
            if isinstance(prop.value, Expression) else prop.value
        prop.setter(node.target, prop.name, value)


def bind_true(node: BindingNode, _: RenderingContext):
    """Rendering pipe: creates binding"""
    if node.when_true:
        binding = ExpressionBinding(lambda _: binding_true_callback(node), node.when_true, node.node_globals)
        binding.bind(node.execute_on_bind)
        node.binding = binding


def binding_true_callback(node: BindingNode):
    value = execute(node.when_true, node.node_globals)
    if value:
        binding_callback(node)


def create_binding_node(context: RenderingContext) -> BindingNode:
    return BindingNode(context.xml_node, context.node_globals)
