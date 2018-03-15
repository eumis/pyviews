'''Processing of xml nodes and creation of instance nodes'''

from importlib import import_module
from pyviews.core import ioc, CoreError
from pyviews.core.reflection import import_path
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, RenderArgs
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.binding import BindingArgs

class ParsingError(CoreError):
    '''Base error for processing xml nodes'''
    pass

def render(xml_node: XmlNode, args: RenderArgs):
    '''Creates instance node'''
    node = create_node(xml_node, args)
    run_steps(node, args)
    return node

@ioc.inject('convert_to_node')
def create_node(xml_node: XmlNode, node_args: RenderArgs, convert_to_node=None):
    '''Initializes instance node from passed arguments'''
    node_class = _get_node_class(xml_node)
    node = create_inst(node_class, node_args)
    if not isinstance(node, Node):
        node = convert_to_node(node, node_args)
    return node

def _get_node_class(xml_node: XmlNode):
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except KeyError:
        raise ParsingError('Unknown class "{0}.{1}".'.format(module_path, class_name))

def create_inst(inst_class, args: RenderArgs):
    '''Creates class instance with args'''
    args = args.get_args(inst_class)
    return inst_class(*args.args, **args.kwargs)

def convert_to_node(inst, args: RenderArgs):
    '''Wraps instance to instance node and returns it'''
    raise NotImplementedError(
        '''
            convert_to_node is not implemented.
            Add implementation to ioc container with "convert_to_node" key.
        ''')

@ioc.inject('container')
def run_steps(node: Node, args: RenderArgs, container=None):
    '''Runs instance node creation steps'''
    try:
        steps = container.get('rendering_steps', node.__class__)
    except ioc.DependencyError:
        steps = container.get('rendering_steps')

    for run_step in steps:
        run_step(node, args)

def render_step(*args):
    '''Resolves dependencies using global container and passed it with optional parameters'''
    keys = args
    def decorate(func):
        def decorated(node, render_args=None):
            render_args = render_args if render_args else {}
            kwargs = {key: render_args[key] for key in keys}
            return func(node, **kwargs)
        return decorated

    if len(args) == 1 and callable(args[0]):
        keys = []
        return decorate(args[0])
    return decorate

@render_step('xml_node')
def apply_attributes(node, xml_node=None):
    '''Applies xml attributes to instance node and setups bindings'''
    for attr in xml_node.attrs:
        apply_attribute(node, attr)

@ioc.inject('binding_factory')
def apply_attribute(node: Node, attr: XmlAttr, binding_factory=None):
    '''Maps xml attribute to instance node property and setups bindings'''
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        (binding_type, expr_body) = parse_expression(value)
        args = BindingArgs(node, attr, modifier, expr_body)
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

@render_step
def render_children(node):
    '''Calls node's render_children'''
    node.render_children()
