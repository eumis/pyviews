from injectool import dependency, DependencyError

from .xml import XmlNode
from .node import Node


@dependency()
def create_node(xml_node: XmlNode, **init_args) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
    raise DependencyError(xml_node, init_args)


@dependency()
def render(xml_node: XmlNode, **render_args) -> Node:
    """Renders node from xml node"""
    raise DependencyError(xml_node, render_args)
