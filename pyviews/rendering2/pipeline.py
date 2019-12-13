"""Rendering pipeline. Node creation from xml node, attribute setup and binding creation"""

from typing import NamedTuple, List, Callable, Union, Any

from pyviews.core import Node, InstanceNode
from pyviews.core import XmlNode
from .common import RenderingContext
from ..rendering import get_inst_type, create_inst, convert_to_node


class RenderingItem(NamedTuple):
    xml_node: XmlNode
    pipeline: 'RenderingPipeline'
    context: RenderingContext


class RenderingPipeline:
    """Contains data, logic used for render steps"""

    def __init__(self, ):
        self.pipes: List[Callable[[Union[Node, InstanceNode, Any], RenderingContext], None]] = []

    def run(self, context: RenderingContext):
        node = self._create_node(context)
        for pipe in self.pipes:
            pipe(node, context)

    @staticmethod
    def _create_node(context: RenderingContext) -> Node:
        inst_type = get_inst_type(context.xml_node)
        inst = create_inst(inst_type, context)
        if not isinstance(inst, Node):
            inst = convert_to_node(inst, context)
        return inst
