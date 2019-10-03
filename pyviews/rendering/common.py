"""Common functionality for rendering package"""

from pyviews.core import CoreError, InheritedDict, Node


class RenderingError(CoreError):
    """Error for rendering"""


class RenderingContext(dict):
    """Used as rendering arguments container, passed to rendering step"""

    @property
    def node_globals(self) -> InheritedDict:
        """Node globals"""
        return self['node_globals']

    @node_globals.setter
    def node_globals(self, value):
        self['node_globals'] = value

    @property
    def parent_node(self) -> Node:
        """Parent node"""
        return self['parent_node']

    @parent_node.setter
    def parent_node(self, value):
        self['parent_node'] = value
