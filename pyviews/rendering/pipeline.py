"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""

from importlib import import_module
from inspect import Parameter, signature
from typing import Any, Callable, Collection, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from injectool import DependencyError, add_singleton, dependency, resolve

from pyviews.core.error import PyViewsError, ViewInfo, error_handling
from pyviews.core.rendering import InstanceNode, Node, RenderingContext, RenderingError
from pyviews.core.xml import XmlNode
from pyviews.rendering.context import use_context
from pyviews.rendering.views import ViewError, get_view_root

N = TypeVar('N', bound = Node)
RC = TypeVar('RC', bound = RenderingContext)
Pipe = Callable[[N, RC], None]
CreateNode = Callable[[RC], N]


class RenderingPipeline(Generic[N, RC]):
    """Creates and renders node"""

    def __init__(
        self,
        pipes: Optional[List[Pipe[N, RC]]] = None,
        create_node: Optional[CreateNode[RC, N]] = None,
        name: Optional[str] = None
    ):
        self._name: Optional[str] = name
        self._pipes: List[Callable[[N, RC], None]] = pipes if pipes else []
        self._create_node: CreateNode = create_node if create_node else _create_node

    def run(self, context: RenderingContext) -> N:
        """Runs pipeline"""
        pipe: Optional[Pipe] = None
        with use_context(context):
            with error_handling(RenderingError, lambda e: self._add_pipe_info(e, pipe, context)):
                node = self._create_node(context)
                for pipe in self._pipes:
                    pipe(node, context)
                return node

    def _add_pipe_info(self, error: PyViewsError, pipe: Optional[Pipe], context: RenderingContext):
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
    except (KeyError, ImportError, ModuleNotFoundError) as error:
        message = f'Import "{module_path}.{class_name}" is failed.'
        raise RenderingError(message, xml_node.view_info) from error


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
        raise RenderingError(msg_format.format(key_error.args[0])) from key_error
    return args, kwargs


def _get_positional_args(parameters: Collection[Parameter], param_values: dict) -> List[Any]:
    keys = [
        p.name for p in parameters
        if p.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD] and p.default == Parameter.empty
    ]
    return [param_values[key] for key in keys]


def _get_optional_args(parameters: List[Parameter], param_values: dict) -> dict:
    keys = [
        p.name for p in parameters if p.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
        and p.default != Parameter.empty and p.name in param_values
    ]
    return {key: param_values[key] for key in keys}


def get_pipeline(xml_node: XmlNode) -> RenderingPipeline:
    """Resolves pipeline by namespace and name or by namespace"""
    key = f'{xml_node.namespace}.{xml_node.name}'
    try:
        return resolve((RenderingPipeline, key))
    except DependencyError:
        try:
            return resolve((RenderingPipeline, xml_node.namespace))
        except DependencyError as error:
            render_error = RenderingError('RenderingPipeline is not found')
            render_error.add_info('Used keys to resolve pipeline', f'{key}, {xml_node.namespace}')
            raise render_error from error


@dependency
def render_view(view_name: str, context: RenderingContext) -> Node:
    """Renders view"""
    with error_handling(ViewError, lambda e: e.add_view_info(ViewInfo(view_name, None))):
        context.xml_node = get_view_root(view_name)
        return render(context)


@dependency
def render(context: RenderingContext) -> Node:
    """Renders node from xml node"""
    with error_handling(RenderingError, lambda e: e.add_view_info(context.xml_node.view_info)):
        pipeline = get_pipeline(context.xml_node)
        return pipeline.run(context)


def use_pipeline(pipeline: RenderingPipeline, class_path: str):
    """Adds rendering pipeline for class path"""
    add_singleton((RenderingPipeline, class_path), pipeline)
