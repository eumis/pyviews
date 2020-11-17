"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""

from importlib import import_module
from inspect import signature, Parameter
from typing import List, Callable, Union, Type, Tuple, Dict, Any, cast, Collection

from injectool import resolve, DependencyError, dependency, SingletonResolver, get_container

from pyviews.core import Node, InstanceNode, XmlNode
from .common import RenderingContext, RenderingError, use_context
from ..core.error import error_handling, PyViewsError

Pipe = Callable[[Node, Union[RenderingContext, Any]], None]
CreateNode = Callable[[Union[RenderingContext, Any]], Node]


class RenderingPipeline:
    """Creates and renders node"""

    def __init__(self, pipes: List[Pipe] = None, create_node: CreateNode = None, name: str = None):
        self._name: str = name
        self._pipes: List[Pipe] = pipes if pipes else []
        self._create_node: CreateNode = create_node if create_node else _create_node

    def run(self, context: RenderingContext) -> Node:
        """Runs pipeline"""
        pipe: Pipe = None
        with use_context(context):
            with error_handling(RenderingError, lambda e: self._add_pipe_info(e, pipe, context)):
                node = self._create_node(context)
                for pipe in self._pipes:
                    pipe(node, context)
                return node

    def _add_pipe_info(self, error: PyViewsError, pipe: Pipe, context: RenderingContext):
        error.add_view_info(context.xml_node.view_info)
        if pipe:
            try:
                next(info for info in error.infos if info.startswith('Pipe'))
            except StopIteration:
                error.add_info('Pipe', pipe)
                error.add_info('Pipeline', self._name)


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
        message = f'Import "{module_path}.{class_name}" is failed.'
        raise RenderingError(message, xml_node.view_info)


def create_instance(instance_type: Type, context: Union[RenderingContext, dict]):
    """Creates class instance with args"""
    args, kwargs = _get_init_args(instance_type, context)
    return instance_type(*args, **kwargs)


def _get_init_args(inst_type: Type, values: dict) -> Tuple[List, Dict]:
    """Returns tuple with args and kwargs to pass it to inst_type constructor"""
    try:
        parameters = list(signature(inst_type).parameters.values())
        args = _get_positional_args(parameters, values)
        kwargs = _get_optional_args(parameters, values)
    except KeyError as key_error:
        msg_format = 'parameter with key "{0}" is not found in node args'
        raise RenderingError(msg_format.format(key_error.args[0]))
    return args, kwargs


def _get_positional_args(parameters: Collection[Parameter], param_values: dict) -> List[Any]:
    keys = [p.name for p in parameters
            if p.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
            and p.default == Parameter.empty]
    return [param_values[key] for key in keys]


def _get_optional_args(parameters: List[Parameter], param_values: dict) -> dict:
    keys = [p.name for p in parameters
            if p.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
            and p.default != Parameter.empty
            and p.name in param_values]
    return {key: param_values[key] for key in keys}


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


def use_pipeline(pipeline: RenderingPipeline, class_path: str, resolver: SingletonResolver = None):
    """Adds rendering pipeline for class path"""
    if resolver is None:
        container = get_container()
        resolver = cast(SingletonResolver, container.get_resolver(RenderingPipeline))
    resolver.set_value(pipeline, class_path)
