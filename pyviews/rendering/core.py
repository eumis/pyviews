'''Processing of xml nodes and creation of instance nodes'''

from sys import exc_info
from importlib import import_module
from pyviews.core import CoreError
from pyviews.core.ioc import SERVICES as deps, DependencyError
from pyviews.core.reflection import import_path
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, RenderArgs
from pyviews.rendering.setup import NodeSetup
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.binding import BindingArgs

class RenderingError(CoreError):
    '''Error for rendering'''
    pass

def render_old(xml_node: XmlNode, args: RenderArgs) -> Node:
    '''Creates instance node'''
    try:
        node = deps.create_node(xml_node, args)
        node_setup = get_setup(node)
        node.setup(node_setup.setters)
        run_steps(node, args)
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

def create_node_old(xml_node: XmlNode, render_args: RenderArgs) -> Node:
    '''Initializes instance node from passed arguments'''
    inst_type = _get_inst_type(xml_node)
    inst = create_inst_old(inst_type, render_args)
    if not isinstance(inst, Node):
        inst = deps.convert_to_node(inst, render_args)
    return inst

def _get_inst_type(xml_node: XmlNode):
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except (KeyError, ImportError, ModuleNotFoundError):
        message = 'Import "{0}.{1}" is failed.'.format(module_path, class_name)
        raise RenderingError(message, xml_node.view_info)

def create_inst_old(inst_class, args: RenderArgs):
    '''Creates class instance with args'''
    args = args.get_args(inst_class)
    return inst_class(*args.args, **args.kwargs)


def get_setup(node: Node) -> NodeSetup:
    '''Gets node setup for passed node'''
    try:
        return deps.for_(node.inst.__class__).setup
    except DependencyError:
        return deps.for_(node.__class__).setup

def run_steps(node: Node, args: RenderArgs):
    '''Runs instance node creation steps'''
    try:
        steps = deps.for_(node.__class__).rendering_steps
    except DependencyError:
        steps = deps.rendering_steps

    for run_step in steps:
        run_step(node, args)

def render_step(*args):
    '''Resolves dependencies using global container and passed it with optional parameters'''
    keys = args
    def _decorate(func):
        def _decorated(node, render_args=None):
            render_args = render_args if render_args else {}
            kwargs = {key: render_args[key] for key in keys}
            return func(node, **kwargs)
        return _decorated

    if len(args) == 1 and callable(args[0]):
        keys = []
        return _decorate(args[0])
    return _decorate

@render_step('xml_node')
def apply_attributes(node, xml_node=None):
    '''Applies xml attributes to instance node and setups bindings'''
    for attr in xml_node.attrs:
        apply_attribute(node, attr)

def apply_attribute(node: Node, attr: XmlAttr):
    '''Maps xml attribute to instance node property and setups bindings'''
    modifier = get_modifier(attr)
    stripped_value = attr.value.strip() if attr.value else ''
    if is_code_expression(stripped_value):
        (binding_type, expr_body) = parse_expression(stripped_value)
        args = BindingArgs(node, attr, modifier, expr_body)
        apply_binding = deps.binding_factory.get_apply(binding_type, args)
        apply_binding(args)
    else:
        modifier(node, attr.name, attr.value)

def get_modifier(attr: XmlAttr):
    '''Returns modifier for xml attribute'''
    if attr.namespace is None:
        return deps.set_attr
    return import_path(attr.namespace)

@render_step
def render_children(node):
    '''Calls node's render_children'''
    node.render_children()

@render_step('xml_node')
def apply_code(node, xml_node=None):
    '''Sets text for Code node'''
    if not xml_node.text:
        return
    node.text = xml_node.text
