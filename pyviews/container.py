"""Contains interfaces for pyviews dependencies"""

from pyviews.core import XmlNode, Node, Expression
from pyviews.core import Binder
from pyviews.core.ioc import SERVICES


def create_node(xml_node: XmlNode, **init_args) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
    return SERVICES.create_node(xml_node, **init_args)


def render(xml_node: XmlNode, **args) -> Node:
    """Renders node from xml node"""
    return SERVICES.render(xml_node, **args)


def binder() -> Binder:
    """Returns Binder instance"""
    return SERVICES.binder


def expression(code: str) -> Expression:
    """Creates Expression instance"""
    return SERVICES.expression(code)


def namespaces() -> str:
    """Predefined namespaces used in views"""
    return SERVICES.namespaces
