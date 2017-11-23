from collections import namedtuple
from inspect import signature, Parameter
from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.binding import ExpressionBinding

class NodeArgs(dict):
    args_tuple = namedtuple('Args', ['args', 'kwargs'])

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
        return NodeArgs.args_tuple(args, kwargs)

class Node:
    def __init__(self, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        self._child_nodes = []
        self._bindings = []
        self.xml_node = xml_node
        self.globals = ExpressionVars(parent_globals)
        self.globals['node'] = self

    def add_binding(self, binding: ExpressionBinding):
        self._bindings.append(binding)

    def destroy(self):
        self.destroy_children()
        self._destroy_bindings()

    def _destroy_bindings(self):
        for binding in self._bindings:
            binding.destroy()
        self._bindings = []

    @inject('parse')
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
