from pyviews.core import ioc
from pyviews.core.reflection import create_inst, import_path
from pyviews.core.compilation import Expression
from pyviews.core.binding import Binding
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import ObservableDict

class Globals:
    def __init__(self, parent=None):
        super().__init__()
        self._container = ObservableDict()
        self._callbacks = []
        self._parent = parent

    def __getitem__(self, key):
        if key in self._container:
            return self._container[key]
        if self._parent is not None:
            return self._parent[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._container[key] = value

    def own_keys(self):
        return self._container.keys()

    def all_keys(self):
        keys = set(self.own_keys())
        if self._parent is not None:
            keys.update(self._parent.own_keys())
        return keys

    def to_dictionary(self):
        return self._container.copy()

    def to_all_dictionary(self):
        return {key: self[key] for key in self.all_keys()}

class Node:
    def __init__(self, xml_node: XmlNode, parent=None):
        self._destroy = []
        self._child_nodes = []
        self._bindings = []
        self.xml_node = xml_node
        self.globals = Globals(parent)

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
        for xml_node in self.xml_node.children:
            args = self.get_parsing_args(xml_node)
            self._child_nodes.append(parse(xml_node, args))

    def destroy_children(self):
        for child in self._child_nodes:
            child.destroy()
        self._child_nodes = []

    def get_parsing_args(self, xml_node: XmlNode):
        return {'parent': self, 'xml_node': xml_node}

class NodeExpression(Expression):
    def __init__(self, node, code):
        super().__init__(code)
        self._node = node

    def get_parameters(self):
        return {'node_key':self._node, **self._node.globals.to_all_dictionary()}

# Looks like tkinter specific
# from os.path import join as join_path
# def read_xml(view, views_folder='views', view_ext='.xml'):
#     view_path = join_path(views_folder, view + view_ext)
#     return get_root(view_path)

def parse(xml_node: XmlNode, args: dict):
    node = create_node(xml_node, args)
    run_parsing_steps(node)
    return node

@ioc.inject('convert_to_node')
def create_node(xml_node: XmlNode, args: dict, convert_to_node=None):
    node = create_inst(xml_node.module_name, xml_node.class_name, **args)
    if not isinstance(node, Node):
        node = convert_to_node(node, xml_node, args)
    node.xml_node = xml_node
    return node

def convert_to_node(inst, xml_node: XmlNode, args: dict):
    raise NotImplementedError('convert_to_node is not implemented', inst, xml_node, args)

@ioc.inject('container')
def run_parsing_steps(node: Node, container=None):
    parsing_steps = container.get('parsing_steps', node.__class__)
    for run_step in parsing_steps:
        run_step(node)

def parse_attributes(node):
    for attr in node.xml_node.get_attrs():
        parse_attr(node, attr)

def parse_attr(node: Node, attr: XmlAttr):
    modifier = get_modifier(attr)
    value = attr.value
    if is_code_expression(value):
        expression = NodeExpression(node, parse_code_expression(value))
        binding = Binding(node, attr.name, modifier, expression)
        node.add_binding(binding)
    else:
        modifier(node, attr.name, value)

def get_modifier(attr: XmlAttr):
    if attr.namespace is None:
        return set_attr
    return import_path(attr.namespace)

def set_attr(node: Node, name, value):
    node.set_attr(name, value)

def is_code_expression(expression):
    return expression.startswith('{') and expression.endswith('}')

def parse_code_expression(expression):
    return expression[1:-1]

def parse_children(node):
    node.parse_children()

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
