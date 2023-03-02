"""Common functionality for rendering package"""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Generator, Optional

from injectool import dependency

from pyviews.core.bindable import InheritedDict
from pyviews.core.rendering import Node, RenderingContext
from pyviews.core.xml import XmlNode


@dependency
def get_child_context(xml_node: XmlNode, parent_node: Node, _: RenderingContext) -> RenderingContext:
    """Return"""
    return RenderingContext({
        'parent_node': parent_node,
        'node_globals': InheritedDict(parent_node.node_globals),
        'xml_node': xml_node
    }) # yapf: disable


_CONTEXT_VAR: ContextVar[RenderingContext] = ContextVar('rendering_context')


@contextmanager
def use_context(context: RenderingContext) -> Generator[RenderingContext, None, None]:
    """Stores rendering context to context var"""
    token = _CONTEXT_VAR.set(context)
    try:
        yield context
    finally:
        _CONTEXT_VAR.reset(token)


def get_rendering_context() -> Optional[RenderingContext]:
    """Returns current rendering context"""
    return _CONTEXT_VAR.get(None)


def pass_rendering_context(func):
    """Passes rendering context as default argument"""

    @wraps(func)
    def _decorated(*args, **kwargs):
        ctx = get_rendering_context()
        return func(*args, **kwargs, rendering_context = ctx)

    return _decorated
