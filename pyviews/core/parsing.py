from inspect import signature, Parameter
from re import compile as compile_regex, match
from collections import namedtuple
from pyviews.core import ioc
from pyviews.core.reflection import import_path
from pyviews.core.compilation import Expression, ExpressionVars
from pyviews.core.binding import ExpressionBinding, InstanceTarget, TwoWaysBinding
from pyviews.core.xml import XmlNode, XmlAttr

class NodeArgs(dict):
    def __init__(self, xml_node: XmlNode, parent_node=None):
        super().__init__()
        self['parent_node'] = parent_node
        self['xml_node'] = xml_node
        self['parent_globals'] = None if parent_node is None else parent_node.globals

    def get_args(self, inst_type=None):
        parameters = signature(inst_type).parameters.values()
        args = [self[p.name] for p in parameters if p.default == Parameter.empty]
        kwargs = {p.name: self[p.name] for p in parameters \
                  if p.default != Parameter.empty and p.name in self}
        return namedtuple('Args', ['args', 'kwargs'])(args, kwargs)

class Node:
    def __init__(self, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        self._child_nodes = []
        self._bindings = []
        self.xml_node = xml_node
        self.globals = ExpressionVars(parent_globals)

    def add_binding(self, binding: ExpressionBinding):
        self._bindings.append(binding)

    def destroy(self):
        self.destroy_children()
        self._destroy_bindings()

    def _destroy_bindings(self):
        for binding in self._bindings:
            binding.destroy()
        self._bindings = []

    @ioc.inject('parse')
    def parse_children(self, parse=None):
        self.destroy_children()
        for xml_node in self.xml_node.get_children():
            args = self.get_node_args(xml_node)
            self._child_nodes.append(parse(xml_node, args))

    def destroy_children(self):
        for child in self._child_nodes:
            child.destroy()
        self._child_nodes = []

    def get_node_args(self, xml_node: XmlNode):
        return NodeArgs(xml_node, self)

# Looks like tkinter specific
# from os.path import join as join_path
# def read_xml(view, views_folder='views', view_ext='.xml'):
#     view_path = join_path(views_folder, view + view_ext)
#     return get_root(view_path)

def parse(xml_node: XmlNode, args: NodeArgs):
    node = create_node(xml_node, args)
    run_parsing_steps(node)
    return node

@ioc.inject('convert_to_node')
def create_node(xml_node: XmlNode, node_args: NodeArgs, convert_to_node=None):
    node_class = import_path(xml_node.class_path)
    args = node_args.get_args(node_class)
    node = node_class(*args.args, **args.kwargs)
    if not isinstance(node, Node):
        node = convert_to_node(node, node_args)
    node.xml_node = xml_node
    return node

def convert_to_node(inst, args: NodeArgs):
    raise NotImplementedError('convert_to_node is not implemented', inst, args)

@ioc.inject('container')
def run_parsing_steps(node: Node, container=None):
    try:
        parsing_steps = container.get('parsing_steps', node.__class__)
    except KeyError:
        parsing_steps = container.get('parsing_steps')
    for run_step in parsing_steps:
        run_step(node)

def parse_attributes(node):
    for attr in node.xml_node.get_attrs():
        parse_attr(node, attr)

def parse_attr(node: Node, attr: XmlAttr):
    modifier = get_modifier(attr)
    value = attr.value
    if is_binding_expression(value):
        (expr, converter_key) = parse_binding_expression(value)
        expression = Expression(expr)
        converter = node.globals[converter_key] if node.globals.has_key(converter_key) else None
        binding = TwoWaysBinding(node, attr.name, modifier, converter, expression)
        binding.bind(node.globals)
        node.add_binding(binding)
    elif is_code_expression(value):
        expression = Expression(parse_code_expression(value))
        target = InstanceTarget(node, attr.name, modifier)
        binding = ExpressionBinding(target, expression)
        binding.bind(node.globals)
        node.add_binding(binding)
    else:
        modifier(node, attr.name, value)

@ioc.inject('set_attr')
def get_modifier(attr: XmlAttr, set_attr=None):
    if attr.namespace is None:
        return set_attr
    return import_path(attr.namespace)

_binding_regex = compile_regex('{[a-zA-Z_]*\{.*\}\}')
def is_binding_expression(expression):
    return _binding_regex.fullmatch(expression) != None

_code_regex = compile_regex('\{.*\}')
def is_code_expression(expression):
    return _code_regex.fullmatch(expression) != None

def parse_code_expression(expression):
    return expression[1:-1]

def parse_binding_expression(expression):
    code_expression = parse_code_expression(expression)
    [converter, expression] = code_expression.split('{', 1)
    return (expression[:-1], converter)

def parse_children(node):
    node.parse_children()

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
ioc.register_value('set_attr', setattr)
