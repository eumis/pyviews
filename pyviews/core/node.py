'''Core classes for creation from xml nodes'''

from collections import namedtuple
from inspect import signature, Parameter
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
    '''Contains bindings and instance rendered from xml node'''
    def __init__(self, xml_node: XmlNode, *args, **kwargs):
        self._child_nodes = []
        self._bindings = []
        self._xml_node = xml_node
        self._globals = InheritedDict({'node': self})
        self._instance = None

    @property
    def xml_node(self):
        '''Returns xml node'''
        return self._xml_node

    @property
    def globals(self) -> InheritedDict:
        '''Values used with expression executing'''
        return self._globals

    @property
    def inst(self):
        '''Returns rendered instance'''
        return self._instance

    def add_binding(self, binding: Binding):
        '''Stores binding'''
        binding.add_error_info = lambda error: error.add_view_info(self._xml_node.view_info)
        self._bindings.append(binding)
