"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""
from sys import exc_info
from typing import Optional

from pyviews.binding import Binder
from pyviews.core import XmlNode, XmlAttr, CoreError
from pyviews.core import Node, InstanceNode, import_path
from pyviews.core import create_node, render
from injectool import DependencyError, resolve
from pyviews.compilation import is_expression, parse_expression
from .common import RenderingError


class RenderingPipeline:
    """Contains data, logic used for render steps"""

    def __init__(self, steps=None):
        self.steps = steps


def render_node(xml_node: XmlNode, **args) -> Node:
    """Renders node from xml node"""
    try:
        node = create_node(xml_node, **args)
        pipeline = get_pipeline(node)
        run_steps(node, pipeline, **args)
        return node
    except CoreError as error:
        error.add_view_info(xml_node.view_info)
        raise
    except:
        info = exc_info()
        msg = 'Unknown error occurred during rendering'
        error = RenderingError(msg, xml_node.view_info)
        error.add_cause(info[1])
        raise error from info[1]


def get_pipeline(node: Node) -> RenderingPipeline:
    """Gets rendering pipeline for passed node"""
    pipeline = _get_registered_pipeline(node)
    if pipeline is None:
        msg = _get_pipeline_error_message(node)
        raise RenderingError(msg)
    return pipeline


def _get_registered_pipeline(node: Node) -> Optional[RenderingPipeline]:
    params = [node.__class__, None]
    if isinstance(node, InstanceNode):
        params = [node.instance.__class__] + params
    for param in params:
        try:
            return resolve(RenderingPipeline, param)
        except (DependencyError, AttributeError):
            pass
    return None


def _get_pipeline_error_message(node: Node) -> str:
    if isinstance(node, InstanceNode):
        return 'RenderingPipeline is not found for {0} with instance {1}' \
            .format(node.__class__, node.instance.__class__)
    else:
        return 'RenderingPipeline is not found for {0}'.format(node.__class__)


def run_steps(node: Node, pipeline: RenderingPipeline, **args):
    """Runs instance node rendering steps"""
    for step in pipeline.steps:
        result = step(node, pipeline=pipeline, **args)
        if isinstance(result, dict):
            args = {**args, **result}


def apply_attributes(node: Node, **_):
    """Applies xml attributes to instance node and setups bindings"""
    for attr in node.xml_node.attrs:
        apply_attribute(node, attr)


def apply_attribute(node: Node, attr: XmlAttr):
    """Maps xml attribute to instance node property and setups bindings"""
    setter = get_setter(attr)
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        (binding_type, expr_body) = parse_expression(stripped_value)
        resolve(Binder).apply(binding_type, node=node, attr=attr, modifier=setter, expr_body=expr_body)
    else:
        setter(node, attr.name, attr.value)


def get_setter(attr: XmlAttr):
    """Returns modifier for xml attribute"""
    if attr.namespace is None:
        return call_set_attr
    return import_path(attr.namespace)


def call_set_attr(node: Node, key: str, value):
    """Calls node setter"""
    node.set_attr(key, value)


def render_children(node: Node, **child_args):
    """Render node children"""
    for xml_node in node.xml_node.children:
        child = render(xml_node, **child_args)
        node.add_child(child)
