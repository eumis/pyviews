from os.path import join as join_path
import xml.etree.ElementTree as ET
from pyviews.core import ioc
from pyviews.core.reflection import create_inst, import_path
from pyviews.core.compilation import Expression
from pyviews.core.binding import Binding

class XmlNode:
    def __init__(self, element: ET.Element):
        self._element = element
        (self.module_name, self.class_name) = parse_namespace(element.tag)

    def get_children(self):
        return [XmlNode(el) for el in list(self._element)]

    def get_attrs(self):
        return [XmlAttr(attr) for attr in self._element.items()]

class XmlAttr:
    def __init__(self, attr):
        (self.name, self.value) = attr
        self.namespace = None
        if has_namespace(self.name):
            (self.namespace, self.name) = parse_namespace(self.name)

class Node:
    def __init__(self, xml_node: XmlNode, parent: Node = None):
        self._destroy = []
        self._child_nodes = []
        self._view_model = None if parent is None else parent.view_model
        self._bindings = []
        self.xml_node = xml_node
        self.globals = {} if parent is None else parent.globals.copy()

    @property
    def view_model(self):
        return self._view_model

    @view_model.setter
    def view_model(self, value):
        self._view_model = value
        for binding in self._bindings:
            binding.update_prop()

    def add_binding(self, binding: Binding):
        self._bindings.append(binding)

    def destroy(self):
        self.destroy_children()
        for binding in self._bindings:
            binding.destroy()

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
        return {'node_key':self._node, 'vm':self._node.view_model, **self._node.globals}

def read_xml(view, views_folder='views', view_ext='.xml'):
    view_path = join_path(views_folder, view + view_ext)
    root_element = ET.parse(view_path).getroot()
    return XmlNode(root_element)

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

def has_namespace(name):
    return name.startswith('{') and '}' in name

def parse_namespace(name):
    if not has_namespace(name):
        raise ParsingError("Name " + name + "doesn't contain namespace")
    splitted = name.split('}', maxsplit=1)
    namespace = splitted[0][1:]
    name = splitted[1]
    return (namespace, name)

class ParsingError(Exception):
    pass

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('parse', parse)
ioc.register_value('parsing_steps', [parse_attributes, parse_children])
