from injectool import dependency, DependencyError

from .xml import XmlNode
from .node import Node


@dependency()
def create_node(xml_node: XmlNode, context: dict) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
    raise DependencyError(xml_node, context)


@dependency()
def render(xml_node: XmlNode, context: dict) -> Node:
    """Renders node from xml node"""
    raise DependencyError(xml_node, context)
