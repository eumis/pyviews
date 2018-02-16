'''Processing of xml nodes and creation of instance nodes'''

from importlib import import_module
from pyviews.core import ioc, CoreError
from pyviews.core.reflection import import_path
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, NodeArgs
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.binding import BindingFactory

class ParsingError(CoreError):
    '''Base error for processing xml nodes'''
    pass

def parse(xml_node: XmlNode, args: NodeArgs):
    '''Creates instance node'''
    node = create_node(xml_node, args)
    run_parsing_steps(node)
    return node

@ioc.inject('convert_to_node')
def create_node(xml_node: XmlNode, node_args: NodeArgs, convert_to_node=None):
    '''Initializes instance node from passed arguments'''
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        node_class = import_module(module_path).__dict__[class_name]
    except KeyError:
        raise ParsingError('Unknown class "{0}.{1}".'.format(module_path, class_name))
    args = node_args.get_args(node_class)
    node = node_class(*args.args, **args.kwargs)
    if not isinstance(node, Node):
        node = convert_to_node(node, node_args)
    return node

def convert_to_node(inst, args: NodeArgs):
    '''Wraps instance to instance node and returns it'''
    raise NotImplementedError('convert_to_node is not implemented', inst, args)

@ioc.inject('container')
def run_parsing_steps(node: Node, container=None):
    '''Runs instance node creation steps'''
    try:
        parsing_steps = container.get('parsing_steps', node.__class__)
    except ioc.DependencyError:
        parsing_steps = container.get('parsing_steps')
    for run_step in parsing_steps:
        run_step(node)

def parse_attributes(node):
    '''Maps xml attributes to instance node properties and setups bindings'''
    for attr in node.xml_node.attrs:
        parse_attr(node, attr)

@ioc.inject('binding_factory')
def parse_attr(node: Node, attr: XmlAttr, binding_factory=None):
    '''Maps xml attribute to instance node property and setups bindings'''
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        (binding_type, expr_body) = parse_expression(value)
        args = BindingFactory.Args(node, attr, modifier, expr_body)
        apply_binding = binding_factory.get_apply(binding_type, args)
        apply_binding(args)
    else:
        modifier(node, attr.name, value)

@ioc.inject('set_attr')
def get_modifier(attr: XmlAttr, set_attr=None):
    '''Returns modifier for xml attribute'''
    if attr.namespace is None:
        return set_attr
    return import_path(attr.namespace)

def parse_children(node):
    '''Calls node's parse_children'''
    node.parse_children()
