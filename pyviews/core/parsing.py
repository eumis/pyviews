'''Processing of xml nodes and creation of instance nodes'''

from importlib import import_module
from re import compile as compile_regex
from collections import namedtuple
from pyviews.core import ioc, CoreError
from pyviews.core.reflection import import_path
from pyviews.core.compilation import Expression
from pyviews.core.binding import ExpressionBinding, InstanceTarget, PropertyExpressionTarget
from pyviews.core.binding import TwoWaysBinding, ObservableBinding
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

def apply_once(args):
    '''Applies "once" binding - expression result is assigned to property without binding'''
    value = Expression(args.expr_body).execute(args.node.globals.to_dictionary())
    args.modifier(args.node, args.attr.name, value)

def apply_oneway(args):
    '''
    Applies "oneway" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    '''
    expression = Expression(args.expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    binding = ExpressionBinding(target, expression, args.node.globals)
    binding.bind()
    args.node.add_binding(binding)

def apply_twoways(args):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (converter_key, expr_body) = parse_expression(args.expr_body)
    expression = Expression(expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    expr_binding = ExpressionBinding(target, expression, args.node.globals)

    target = PropertyExpressionTarget(expression, args.node.globals)
    converter = args.node.globals[converter_key] \
                if args.node.globals.has_key(converter_key) else None
    obs_binding = ObservableBinding(target, args.node, args.attr.name, converter)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    args.node.add_binding(two_ways_binding)

def parse_children(node):
    '''Calls node's parse_children'''
    node.parse_children()

class BindingFactory:
    '''Factory for getting binding applier'''

    Rule = namedtuple('BindingRule', ['suitable', 'apply'])
    Args = namedtuple('BindingArgs', ['node', 'attr', 'modifier', 'expr_body'])

    def __init__(self):
        self._defaults = {
            'once': apply_once,
            'oneway': apply_oneway,
            'twoways': apply_twoways
        }
        self._rules = {}

    def add_rule(self, binding_type, rule):
        '''Adds new rule to factory'''
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].append(rule)

    def get_apply(self, binding_type, args):
        '''returns apply function'''
        rule = self._find_rule(binding_type, args)
        if rule is not None:
            return rule.apply

        if binding_type in self._defaults:
            return self._defaults[binding_type]

        raise ParsingError('There is no rule for binding type {0}'.format(binding_type))

    def _find_rule(self, binding_type, args):
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(args))
        except (KeyError, StopIteration):
            return None

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
ioc.register_value('set_attr', setattr)
ioc.register_value('binding_factory', BindingFactory())
