'''Rendering flow. Node creation from xml node, attribute setup and binding creation'''

from sys import exc_info
from pyviews.core import CoreError
from pyviews.core.ioc import SERVICES as deps, DependencyError
from pyviews.core.reflection import import_path
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, InstanceNode
from pyviews.rendering import RenderingError
from pyviews.rendering.setup import NodeSetup
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.binding import BindingArgs

def render(xml_node: XmlNode, **args) -> Node:
    '''Renders node from xml node'''
    try:
        node = deps.create_node(xml_node, **args)
        node_setup = get_node_setup(node)
        node_setup.apply(node)
        run_steps(node, node_setup)
        return node
    except CoreError as error:
        error.add_view_info(xml_node.view_info)
        raise
    except:
        info = exc_info()
        msg = 'Unknown error occured during rendering'
        error = RenderingError(msg, xml_node.view_info)
        error.add_cause(info[1])
        raise error from info[1]

_DEPS_GETTERS = [
    lambda node: deps.for_(node.instance.__class__),
    lambda node: deps.for_(node.__class__),
    lambda node: deps
]
def get_node_setup(node: Node) -> NodeSetup:
    '''Gets node setup for passed node'''
    for get_deps in _DEPS_GETTERS:
        try:
            return get_deps(node).setup
        except (DependencyError, AttributeError):
            pass
    if isinstance(node, InstanceNode):
        msg = 'NodeSetup is not found for {0} with instance {1}'\
              .format(node.__class__, node.instance.__class__)
    else:
        msg = 'NodeSetup is not found for {0}'.format(node.__class__)
    raise RenderingError(msg)

def run_steps(node: Node, node_setup: NodeSetup, **args):
    '''Runs instance node rendering steps'''
    for step in node_setup.render_steps:
        step(node, node_setup=node_setup, **args)

def apply_attributes(node: Node):
    '''Applies xml attributes to instance node and setups bindings'''
    for attr in node.xml_node.attrs:
        apply_attribute(node, attr)

def apply_attribute(node: Node, attr: XmlAttr):
    '''Maps xml attribute to instance node property and setups bindings'''
    setter = get_setter(attr)
    stripped_value = attr.value.strip() if attr.value else ''
    if is_code_expression(stripped_value):
        (binding_type, expr_body) = parse_expression(stripped_value)
        args = BindingArgs(node, attr, setter, expr_body)
        apply_binding = deps.binding_factory.get_apply(binding_type, args)
        apply_binding(args)
    else:
        setter(node, attr.name, attr.value)

def get_setter(attr: XmlAttr):
    '''Returns modifier for xml attribute'''
    if attr.namespace is None:
        return default_setter
    return import_path(attr.namespace)

def default_setter(node: Node, key: str, value):
    '''Calls node setter'''
    node.setter(node, key, value)

def render_children(node: Node, node_setup: NodeSetup = None, **args):
    '''Render node children'''
    child_args = node_setup.get_child_init_args(node, **args)
    for xml_node in node.xml_node.children:
        deps.render(xml_node, **child_args)
