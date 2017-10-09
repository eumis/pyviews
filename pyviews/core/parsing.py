from pyviews.core import ioc
from pyviews.core.reflection import create_inst, import_path
from pyviews.core.compilation import Expression, ExpressionVars
from pyviews.core.binding import Binding, BindingTarget
from pyviews.core.xml import XmlNode, XmlAttr

class NodeArgs:
    def __init__(self, xml_node: XmlNode, parent_node=None):
        super().__init__()
        self.parent_node = parent_node
        self.xml_node = xml_node

    def get_args(self, inst_type=None):
        return [self.xml_node]

    def get_kwargs(self, inst_type=None):
        return {'parent_node': self.parent_node}

class Node:
    def __init__(self, xml_node: XmlNode, parent_node=None):
        self._child_nodes = []
        self._bindings = []
        self.xml_node = xml_node
        self.globals = ExpressionVars(None if parent_node is None else parent_node.globals)

    def add_binding(self, binding: Binding):
        self._bindings.append(binding)

    def destroy(self):
        self.destroy_children()
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
def create_node(xml_node: XmlNode, args: NodeArgs, convert_to_node=None):
    node = create_inst(
        xml_node.module_name, xml_node.class_name,
        args.get_args(), args.get_kwargs())
    if not isinstance(node, Node):
        node = convert_to_node(node, args)
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
    if is_code_expression(value):
        expression = Expression(parse_code_expression(value))
        target = BindingTarget(node, attr.name, modifier)
        binding = Binding(target, expression)
        binding.bind(node.globals)
        node.add_binding(binding)
    else:
        modifier(node, attr.name, value)

def get_modifier(attr: XmlAttr):
    if attr.namespace is None:
        return setattr
    return import_path(attr.namespace)

def is_code_expression(expression):
    return expression.startswith('{') and expression.endswith('}')

def parse_code_expression(expression):
    return expression[1:-1]

def parse_children(node):
    node.parse_children()

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
