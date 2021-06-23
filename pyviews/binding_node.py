from typing import Any, NamedTuple, Union, List

from pyviews.binding import ExpressionBinding
from pyviews.core import XmlNode, InheritedDict, Node, Setter, Binding
from pyviews.expression import is_expression, parse_expression, Expression, execute
from pyviews.pipes import get_setter
from pyviews.rendering import RenderingPipeline, RenderingContext


class BindingProperty(NamedTuple):
    name: str
    setter: Setter
    value: Union[Expression, Any]


class BindingNode(Node):
    def __init__(self, xml_node: XmlNode,
                 node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.properties: List[BindingProperty] = []
        self.target: Any = None
        self.when: Expression = None
        self.execute_on_bind: bool = True
        self.binding: Binding = None

    def destroy(self):
        self.binding.destroy()
        self.binding = None


def get_binding_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        set_target,
        bind
    ], name='container pipeline', create_node=create_binding_node)


def apply_attributes(node: BindingNode, _: RenderingContext):
    """Rendering pipe: records attributes to bind"""
    for attr in node.xml_node.attrs:
        value = attr.value.strip() if attr.value else ''
        if is_expression(value):
            value = Expression(parse_expression(value)[1])
        if attr.name == 'when':
            node.when = value
        elif attr.name in node.__dict__:
            setattr(node, attr.name, execute(value, node.node_globals.to_dictionary()))
        else:
            setter = get_setter(attr)
            node.properties.append(BindingProperty(attr.name, setter, value))


def set_target(node: BindingNode, context: RenderingContext):
    """Rendering pipe: sets target"""
    if node.target is None:
        node.target = context.parent_node


def bind(node: BindingNode, _: RenderingContext):
    """Rendering pipe: creates binding"""
    binding = ExpressionBinding(lambda _: binding_callback(node), node.when, node.node_globals)
    binding.bind(node.execute_on_bind)
    node.binding = binding


def binding_callback(node: BindingNode):
    for prop in node.properties:
        value = execute(prop.value, node.node_globals.to_dictionary()) \
            if isinstance(prop.value, Expression) else prop.value
        prop.setter(node.target, prop.name, value)


def create_binding_node(context: RenderingContext) -> BindingNode:
    return BindingNode(context.xml_node, context.node_globals)
