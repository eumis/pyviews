'''Core classes for creation from xml nodes'''

from collections import namedtuple
from inspect import signature, Parameter
from typing import List, Callable, Any
from pyviews.core import CoreError
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from pyviews.core.binding import Binding

class RenderArgs(dict):
    '''Wraps arguments for children nodes creations'''

    Result = namedtuple('Args', ['args', 'kwargs'])

    def __init__(self, xml_node: XmlNode, parent_node=None):
        super().__init__()
        self['parent_node'] = parent_node
        self['xml_node'] = xml_node
        self['parent_context'] = None

    def get_args(self, inst_type):
        '''Returns tuple with args and kwargs to pass it to inst_type constructor'''
        try:
            parameters = signature(inst_type).parameters.values()
            args = [self[p.name] for p in parameters if p.default == Parameter.empty]
            kwargs = {p.name: self[p.name] for p in parameters \
                      if p.default != Parameter.empty and p.name in self}
        except KeyError as key_error:
            msg_format = 'parameter with key "{0}" is not found in node args'
            raise CoreError(msg_format.format(key_error.args[0]))
        return RenderArgs.Result(args, kwargs)

class Node:
    '''Represents node with properties and bindings created from xml node'''
    def __init__(self, xml_node: XmlNode, globals: InheritedDict = None):
        self._child_nodes = []
        self._bindings = []
        self._xml_node = xml_node
        self._globals = InheritedDict({'node': self})
        if globals:
            self._globals.inherit(globals)
        self._setters = []

    @property
    def xml_node(self) -> XmlNode:
        '''Returns xml node'''
        return self._xml_node

    @property
    def globals(self) -> InheritedDict:
        '''Values used with expression executing'''
        return self._globals

    @property
    def setters(self) -> List:
        '''Returns property setters'''
        return self._setters

    def setup(self, setters: List = None):
        '''Setups node'''
        if setters:
            self._setters = setters

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
