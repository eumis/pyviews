"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""
from sys import exc_info
from typing import Optional, NamedTuple, List, Callable, Union
from injectool import DependencyError, resolve, dependency

from pyviews.core import XmlNode, XmlAttr, CoreError
from pyviews.core import Node, InstanceNode, import_path

# def _get_registered_pipeline(node: Node) -> Optional[RenderingPipeline]:
#     params = [node.__class__, None]
#     if isinstance(node, InstanceNode):
#         params = [node.instance.__class__] + params
#     for param in params:
#         try:
#             return resolve(RenderingPipeline, param)
#         except (DependencyError, AttributeError):
#             pass
#     return None
#
#
# def _get_pipeline_error_message(node: Node) -> str:
#     if isinstance(node, InstanceNode):
#         return 'RenderingPipeline is not found for {0} with instance {1}' \
#             .format(node.__class__, node.instance.__class__)
#     return 'RenderingPipeline is not found for {0}'.format(node.__class__)
#
#
