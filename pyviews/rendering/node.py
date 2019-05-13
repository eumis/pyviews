"""Module contains Code node"""

from importlib import import_module
from inspect import signature, Parameter
from typing import Tuple, List, Dict
from pyviews.core.node import Node, InstanceNode
from pyviews.core.xml import XmlNode
from pyviews.core.observable import InheritedDict
from .common import RenderingError


def create_node(xml_node: XmlNode, **init_args):
    """Creates node from xml node using namespace as module and tag name as class name"""
    inst_type = get_inst_type(xml_node)
    init_args['xml_node'] = xml_node
    inst = create_inst(inst_type, **init_args)
    if not isinstance(inst, Node):
        inst = convert_to_node(inst, **init_args)
    return inst


def get_inst_type(xml_node: XmlNode):
    """Returns type by xml node"""
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except (KeyError, ImportError, ModuleNotFoundError):
        message = 'Import "{0}.{1}" is failed.'.format(module_path, class_name)
        raise RenderingError(message, xml_node.view_info)


def create_inst(inst_type, **init_args):
    """Creates class instance with args"""
    args, kwargs = get_init_args(inst_type, init_args)
    return inst_type(*args, **kwargs)


def get_init_args(inst_type, init_args: dict, add_kwargs=False) -> Tuple[List, Dict]:
    """Returns tuple with args and kwargs to pass it to inst_type constructor"""
    try:
        parameters = signature(inst_type).parameters.values()
        args_keys = [p.name for p in parameters
                     if p.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
                     and p.default == Parameter.empty]
        args = [init_args[key] for key in args_keys]
        kwargs = _get_var_kwargs(parameters, args_keys, init_args) \
            if add_kwargs else \
            _get_kwargs(parameters, init_args)
    except KeyError as key_error:
        msg_format = 'parameter with key "{0}" is not found in node args'
        raise RenderingError(msg_format.format(key_error.args[0]))
    return args, kwargs


def _get_var_kwargs(parameters: list, args_keys: list, init_args: dict) -> dict:
    try:
        next(p for p in parameters if p.kind == Parameter.VAR_KEYWORD)
    except StopIteration:
        return _get_kwargs(parameters, init_args)
    else:
        kwargs = {key: value for key, value in init_args.items() if key not in args_keys}
    return kwargs


def _get_kwargs(parameters: list, init_args: dict) -> dict:
    init_parameters = [p for p in parameters
                       if p.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
                       and p.default != Parameter.empty
                       and p.name in init_args]
    return {
        p.name: init_args[p.name] for p in init_parameters
    }


def convert_to_node(instance, xml_node: XmlNode, node_globals: InheritedDict = None) \
        -> InstanceNode:
    """Wraps passed instance with InstanceNode"""
    return InstanceNode(instance, xml_node, node_globals)
