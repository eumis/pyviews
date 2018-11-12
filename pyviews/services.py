'''Contains interfaces for pyviews dependencies'''

from pyviews.core.xml import XmlNode
from pyviews.core.ioc import SERVICES
from pyviews.core.node import Node
from pyviews.rendering.binding import BindingFactory

def create_node(xml_node: XmlNode, **init_args) -> Node:
    '''Creates node from xml node using namespace as module and tag name as class name'''
    return SERVICES.create_node(xml_node, **init_args)

def render(xml_node: XmlNode, **args) -> Node:
    '''Renders node from xml node'''
    return SERVICES.render(xml_node, **args)

def binding_factory() -> BindingFactory:
    '''Returns BindingFactory instance'''
    return SERVICES.binding_factory
