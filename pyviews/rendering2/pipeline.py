"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""
from importlib import import_module
from inspect import signature, Parameter
from typing import NamedTuple, List, Callable, Union, Any, Type, Tuple, Dict

from injectool import resolve

from pyviews.core import Node, InstanceNode, XmlNode
from .common import RenderingContext, RenderingError


class RenderingItem(NamedTuple):
    """Tuple with rendering pipeline and rendering context"""
    pipeline: 'RenderingPipeline'
    context: RenderingContext


class RenderingPipeline:
    """Creates and renders node"""

    def __init__(self, pipes=None):
        self._pipes: List[Callable[[Union[Node, InstanceNode, Any], RenderingContext], None]] = pipes if pipes else []

    def run(self, context: RenderingContext, render_items: Callable[[List[RenderingItem]], None]) -> Node:
        node = self._create_node(context)
        for pipe in self._pipes:
            pipe(node, context, render_items)
        return node

    @staticmethod
    def _create_node(context: RenderingContext) -> Node:
        inst_type = get_type(context.xml_node)
        inst = create_instance(inst_type, context)
        if not isinstance(inst, Node):
            inst = InstanceNode(inst, context.xml_node, context.node_globals)
        return inst


def get_type(xml_node: XmlNode) -> Type:
    """Returns instance type for xml node"""
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except (KeyError, ImportError, ModuleNotFoundError):
        message = 'Import "{0}.{1}" is failed.'.format(module_path, class_name)
        raise RenderingError(message, xml_node.view_info)


def create_instance(instance_type: Type, context: RenderingContext):
    """Creates class instance with args"""
    args, kwargs = _get_init_args(instance_type, context)
    return instance_type(*args, **kwargs)


def _get_init_args(inst_type, init_args: RenderingContext, add_kwargs=False) -> Tuple[List, Dict]:
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


def get_pipeline(xml_node: XmlNode) -> RenderingPipeline:
    key = f'{xml_node.namespace}.{xml_node.name}'
    return resolve(RenderingPipeline, key)
