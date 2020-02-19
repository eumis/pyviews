"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""

from importlib import import_module
from inspect import signature, Parameter
from typing import List, Callable, Union, Type, Tuple, Dict

from injectool import resolve, DependencyError, dependency

from pyviews.core import Node, InstanceNode, XmlNode
from .common import RenderingContext, RenderingError
from ..core.error import error_handling, PyViewsError

Pipe = Callable[[RenderingContext], None]


class RenderingPipeline:
    """Creates and renders node"""

    def __init__(self, pipes=None, create_node=None):
        self._pipes: List[Pipe] = pipes if pipes else []
        self._create_node: Callable[
            [RenderingContext], Node] = create_node if create_node else _create_node

    def run(self, context: RenderingContext) -> Node:
        """Runs pipeline"""
        pipe = None
        with error_handling(RenderingError, lambda e: self._add_pipe_info(e, pipe, context)):
            node = self._create_node(context)
            for pipe in self._pipes:
                pipe(node, context)
            return node

    @staticmethod
    def _add_pipe_info(error: PyViewsError, pipe: Pipe, context: RenderingContext):
        error.add_view_info(context.xml_node.view_info)
        if pipe:
            try:
                next(info for info in error.infos if info.startswith('Pipe'))
            except StopIteration:
                error.add_info('Pipe', pipe)


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


def create_instance(instance_type: Type, context: Union[RenderingContext, dict]):
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
    """Resolves pipeline by namespace and name or by namespace"""
    key = f'{xml_node.namespace}.{xml_node.name}'
    try:
        return resolve(RenderingPipeline, key)
    except DependencyError:
        try:
            return resolve(RenderingPipeline, xml_node.namespace)
        except DependencyError as error:
            render_error = RenderingError('RenderingPipeline is not found')
            render_error.add_info('Used keys to resolve pipeline', f'{key}, {xml_node.namespace}')
            raise render_error from error


@dependency
def render(context: RenderingContext) -> Node:
    """Renders node from xml node"""
    with error_handling(RenderingError, lambda e: e.add_view_info(context.xml_node.view_info)):
        pipeline = get_pipeline(context.xml_node)
        return pipeline.run(context)
