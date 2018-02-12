'''Processing of xml nodes and creation of instance nodes'''

from importlib import import_module
from re import compile as compile_regex
from pyviews.core import ioc, CoreError
from pyviews.core.reflection import import_path
from pyviews.core.compilation import Expression
from pyviews.core.binding import ExpressionBinding, InstanceTarget, TwoWaysBinding, ObservableBinding, PropertyExpressionTarget
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, NodeArgs

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
    except KeyError:
        parsing_steps = container.get('parsing_steps')
    for run_step in parsing_steps:
        run_step(node)

def parse_attributes(node):
    '''Maps xml attributes to instance node properties and setups bindings'''
    for attr in node.xml_node.attrs:
        parse_attr(node, attr)

@ioc.inject('container')
def parse_attr(node: Node, attr: XmlAttr, container=None):
    '''Maps xml attribute to instance node property and setups bindings'''
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        (binding_type, expr_body) = parse_expression(value)
        apply_binding = container.get(binding_type)
        apply_binding(expr_body, node, attr, modifier)
    else:
        modifier(node, attr.name, value)

@ioc.inject('set_attr')
def get_modifier(attr: XmlAttr, set_attr=None):
    '''Returns modifier for xml attribute'''
    if attr.namespace is None:
        return set_attr
    return import_path(attr.namespace)

EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_]{1,}\:){0,1}\{.*\}')
def is_code_expression(expression):
    '''Return true if passed value is binding expression'''
    return EXPRESSION_REGEX.fullmatch(expression) != None

def parse_expression(expression):
    '''Returns tuple with binding type and expression body'''
    if expression[0] != '{':
        [binding_type, expression] = expression.split(':', 1)
    elif expression.endswith('}}'):
        binding_type = 'twoways'
    else:
        binding_type = 'oneway'
    return (binding_type, expression[1:-1])

def apply_once(expr_body, node, attr, modifier):
    '''Applies "once" binding - expression result is assigned to property without binding'''
    value = Expression(expr_body).execute(node.globals.to_dictionary())
    modifier(node, attr.name, value)

def apply_oneway(expr_body, node, attr, modifier):
    '''
    Applies "oneway" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    '''
    expression = Expression(expr_body)
    target = InstanceTarget(node, attr.name, modifier)
    binding = ExpressionBinding(target, expression, node.globals)
    binding.bind()
    node.add_binding(binding)

@ioc.inject('container')
def apply_twoways(expr_body, node, attr, modifier, container=None):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (converter_key, expr_body) = parse_expression(expr_body)
    expression = Expression(expr_body)
    target = InstanceTarget(node, attr.name, modifier)
    expr_binding = ExpressionBinding(target, expression, node.globals)

    target = PropertyExpressionTarget(expression, node.globals)
    converter = node.globals[converter_key] if node.globals.has_key(converter_key) else None
    obs_binding = ObservableBinding(target, node, attr.name, converter)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    node.add_binding(two_ways_binding)

def parse_children(node):
    '''Calls node's parse_children'''
    node.parse_children()

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
ioc.register_value('set_attr', setattr)
ioc.register_value('once', apply_once)
ioc.register_value('oneway', apply_oneway)
ioc.register_value('twoways', apply_twoways)
