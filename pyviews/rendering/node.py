'''Module contains Code node'''

from importlib import import_module
from inspect import signature, Parameter
from typing import Tuple, List, Dict
from pyviews.core.node import Node, InstanceNode
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from pyviews.rendering import RenderingError

def create_node(xml_node: XmlNode, **init_args):
    '''Creates node from xml node using namespace as module and tag name as class name'''
    inst_type = _get_inst_type(xml_node)
    init_args['xml_node'] = xml_node
    inst = create_inst(inst_type, **init_args)
    if not isinstance(inst, Node):
        inst = convert_to_node(inst, **init_args)
    return inst

def _get_inst_type(xml_node: XmlNode):
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except (KeyError, ImportError, ModuleNotFoundError):
        message = 'Import "{0}.{1}" is failed.'.format(module_path, class_name)
        raise RenderingError(message, xml_node.view_info)

def create_inst(inst_type, **init_args):
    '''Creates class instance with args'''
    args, kwargs = get_init_args(inst_type, **init_args)
    return inst_type(*args, **kwargs)

def get_init_args(inst_type, **init_args) -> Tuple[List, Dict]:
    '''Returns tuple with args and kwargs to pass it to inst_type constructor'''
    try:
        parameters = signature(inst_type).parameters.values()
        args = [init_args[p.name] for p in parameters if p.default == Parameter.empty]
        kwargs = {p.name: init_args[p.name] for p in parameters \
                    if p.default != Parameter.empty and p.name in init_args}
    except KeyError as key_error:
        msg_format = 'parameter with key "{0}" is not found in node args'
        raise RenderingError(msg_format.format(key_error.args[0]))
    return (args, kwargs)

def convert_to_node(instance, xml_node: XmlNode, node_globals: InheritedDict = None) -> InstanceNode:
    '''Wraps passed instance with InstanceNode'''
    return InstanceNode(instance, xml_node, node_globals)
