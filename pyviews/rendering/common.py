"""Common functionality for rendering package"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Union

from injectool import dependency

from pyviews.core import PyViewsError, InheritedDict, Node, XmlNode, InstanceNode, ViewInfo


class RenderingError(PyViewsError):
    """Error for rendering"""

    def __init__(self, message: str = None, view_info: ViewInfo = None):
        super().__init__(message=message, view_info=view_info)


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


@dependency
def get_child_context(xml_node: XmlNode, parent_node: Node,
                      _: RenderingContext) -> RenderingContext:
    """Return"""
    return RenderingContext({
        'parent_node': parent_node,
        'node_globals': InheritedDict(parent_node.node_globals),
        'xml_node': xml_node
    })


_CONTEXT_VAR: ContextVar[RenderingContext] = ContextVar('rendering_context')


@contextmanager
def use_context(context: RenderingContext) -> RenderingContext:
    """Stores rendering context to context var"""
    token = _CONTEXT_VAR.set(context)
    try:
        yield context
    finally:
        _CONTEXT_VAR.reset(token)


def get_rendering_context() -> RenderingContext:
    """Returns current rendering context"""
    return _CONTEXT_VAR.get(None)


def pass_rendering_context(func):
    """Passes rendering context as default argument"""

    @wraps(func)
    def _decorated(*args, **kwargs):
        ctx = get_rendering_context()
        return func(*args, **kwargs, rendering_context=ctx)

    return _decorated
