"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""

from typing import NamedTuple, List, Callable, Union, Any

from pyviews.core import Node, InstanceNode
from .common import RenderingContext
from ..rendering import get_inst_type, create_inst, convert_to_node


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
        inst_type = get_inst_type(context.xml_node)
        inst = create_inst(inst_type, context)
        if not isinstance(inst, Node):
            inst = convert_to_node(inst, context)
        return inst
