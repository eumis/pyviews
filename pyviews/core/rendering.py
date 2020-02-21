"""Core classes for creation from xml nodes"""

from functools import partial
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
        # noinspection PyTypeChecker
        self.set_attr: Callable[[str, Any], None] = partial(setattr, self)
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

    def add_binding(self, binding: Binding):
        """Stores binding"""
        binding.add_error_info = lambda error: error.add_view_info(self._xml_node.view_info)
        self._bindings.append(binding)

    def add_child(self, child: 'Node'):
        """Adds rendered child"""
        self._children.append(child)

    def add_children(self, children: List['Node']):
        """Adds list of rendered children"""
        self._children = self._children + children

    def destroy(self):
        """Destroys node"""
        self.destroy_children()
        self.destroy_bindings()
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


class InstanceNode(Node):
    """Represents Node that wraps instance created from xml node"""

    def __init__(self, instance: Any, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals)
        self._instance = instance
        self.set_attr = partial(_instance_attr_setter, self)

    @property
    def instance(self):
        """Returns rendered instance"""
        return self._instance


def _instance_attr_setter(node: InstanceNode, key, value):
    ent = node if hasattr(node, key) else node.instance
    setattr(ent, key, value)


Setter = Callable[[Node, str, Any], None]
