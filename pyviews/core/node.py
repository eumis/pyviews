"""Core classes for creation from xml nodes"""

from inspect import signature, Parameter
from typing import Any, List, Callable

from .binding import Binding
from .observable import InheritedDict
from .xml import XmlNode


class Node:
    """Represents node with properties and bindings created from xml node"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        self._children: List[Node] = []
        self._bindings: List[Binding] = []
        self._xml_node: XmlNode = xml_node
        self._globals: InheritedDict = InheritedDict() if node_globals is None else node_globals
        self._globals['node'] = self
        self.attr_setter = _attr_setter
        self.properties = {}
        self.on_destroy = lambda node: None

    @property
    def xml_node(self) -> XmlNode:
        """Returns xml node"""
        return self._xml_node

    @property
    def node_globals(self) -> InheritedDict:
        """Values used with expression executing"""
        return self._globals

    @property
    def children(self) -> List:
        """Returns child nodes"""
        return self._children

    def set_attr(self, key: str, value):
        """Sets node attribute. Can be customized by attr_setter property"""
        self.attr_setter(self, key, value)

    def add_binding(self, binding: Binding):
        """Stores binding"""
        binding.add_error_info = lambda error: error.add_view_info(self._xml_node.view_info)
        self._bindings.append(binding)

    def add_child(self, child):
        """Adds rendered child"""
        self._children.append(child)

    def add_children(self, children: List):
        """Adds list of rendered children"""
        self._children = self._children + children

    def destroy(self):
        """Destroys node"""
        self.destroy_children()
        self.destroy_bindings()
        if self.on_destroy:
            self.on_destroy(self)

    def destroy_children(self):
        """Destroys and removes all bindings"""
        for child in self._children:
            child.destroy()
        self._children = []

    def destroy_bindings(self):
        """Destroys and removes all bindings"""
        for binding in self._bindings:
            binding.destroy()
        self._bindings = []


def _attr_setter(node: Node, key, value):
    if key in node.properties:
        node.properties[key].set(value)
    else:
        setattr(node, key, value)


class InstanceNode(Node):
    """Represents Node that wraps instance created from xml node"""

    def __init__(self, instance: Any, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals)
        self._instance = instance
        self.attr_setter = _inst_attr_setter

    @property
    def instance(self):
        """Returns rendered instance"""
        return self._instance


def _inst_attr_setter(node: InstanceNode, key, value):
    if key in node.properties:
        node.properties[key].set(value)
    else:
        ent = node if hasattr(node, key) else node.instance
        setattr(ent, key, value)


class Property:
    """Class to define property"""

    def __init__(self, name, setter=None, node: Node = None):
        self.name = name
        self._value = None
        self._setter = None
        if setter:
            args_count = len([p for p in signature(setter).parameters.values() if p.default == Parameter.empty])
            self._setter = setter if args_count == 3 else \
                lambda nd, value, previous: setter(nd, value)
        self._node = node

    def get(self):
        """Returns value"""
        return self._value

    def set(self, value):
        """Sets value"""
        self._value = self._setter(self._node, value, self._value) if self._setter else value

    def new(self, node: Node):
        """Creates property for node"""
        return Property(self.name, self._setter, node)


Modifier = Callable[[Node, str, Any], None]
