'''Core classes for creation from xml nodes'''

from typing import Callable, Any
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from pyviews.core.binding import Binding

class Node:
    '''Represents node with properties and bindings created from xml node'''
    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        self._child_nodes = []
        self._bindings = []
        self._xml_node = xml_node
        self._globals = InheritedDict({'node': self})
        if node_globals:
            self._globals.inherit(node_globals)
        self.setter = None

    @property
    def xml_node(self) -> XmlNode:
        '''Returns xml node'''
        return self._xml_node

    @property
    def globals(self) -> InheritedDict:
        '''Values used with expression executing'''
        return self._globals

    def add_binding(self, binding: Binding):
        '''Stores binding'''
        binding.add_error_info = lambda error: error.add_view_info(self._xml_node.view_info)
        self._bindings.append(binding)

    def destroy_bindings(self):
        '''Destroys and removes all bindings'''
        for binding in self._bindings:
            binding.destroy()
        self._bindings = []

class InstanceNode(Node):
    '''Represents Node that wraps instance created from xml node'''
    def __init__(self, instance: Any, xml_node: XmlNode, globals: InheritedDict = None):
        super().__init__(xml_node, globals)
        self._instance = instance

    @property
    def instance(self):
        '''Returns rendered instance'''
        return self._instance

SETTER = Callable[[Node, str, Any], bool]

def setter(func: [[Node, str, Any], bool]):
    '''Calls decorated function and returns True'''
    def _decorated(node, passed_key, value):
        func(node, passed_key, value)
        return True
    return _decorated

def keysetter(key: str):
    '''Calls decorated function for passed key and returns True, otherwise returns False'''
    def _decorate(func: SETTER):
        def _decorated(node, passed_key, value):
            if key == passed_key:
                func(node, passed_key, value)
                return True
            return False
        return _decorated
    return _decorate
