"""Common functionality for rendering package"""
from typing import Union

from pyviews.core import CoreError, InheritedDict, Node, XmlNode, InstanceNode


class RenderingError(CoreError):
    """Error for rendering"""


class RenderingContext(dict):
    """Used as rendering arguments container, passed to rendering step"""

    @property
    def node_globals(self) -> InheritedDict:
        """Node globals"""
        return self.get('node_globals', None)

    @node_globals.setter
    def node_globals(self, value):
        self['node_globals'] = value

    @property
    def parent_node(self) -> Union[Node, InstanceNode]:
        """Parent node"""
        return self.get('parent_node', None)

    @parent_node.setter
    def parent_node(self, value: Union[Node, InstanceNode]):
        self['parent_node'] = value

    @property
    def xml_node(self) -> XmlNode:
        """xml node"""
        return self.get('xml_node', None)

    @xml_node.setter
    def xml_node(self, value: XmlNode):
        self['xml_node'] = value
