"""Contains interfaces for pyviews dependencies"""
from injectool import resolve

from pyviews.binding import Binder
from pyviews.core import XmlNode, Node, Expression


def create_node(xml_node: XmlNode, **init_args) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
    return resolve('create_node')(xml_node, **init_args)


def render(xml_node: XmlNode, **args) -> Node:
    """Renders node from xml node"""
    return resolve('render')(xml_node, **args)


def binder() -> Binder:
    """Returns Binder instance"""
    return resolve('binder')


def expression(code: str) -> Expression:
    """Creates Expression instance"""
    return resolve('expression')(code)


def namespaces() -> str:
    """Predefined namespaces used in views"""
    return resolve('namespaces')
