"""Module with setters"""

from typing import Any, Iterable, NamedTuple, Union

from injectool import resolve

from pyviews.core.reflection import import_path
from pyviews.core.rendering import InstanceNode, Node


def import_global(node: Node, key: str, path: Any):
    """Import passed module, class, function full name and stores it to node's globals"""
    node.node_globals[key] = import_path(path)


def inject_global(node: Node, global_key: str, inject_key: Any):
    """Resolves passed dependency and stores it to node's globals"""
    value = resolve(inject_key)
    set_global(node, global_key, value)


def set_global(node: Node, key: str, value: Any):
    """Adds passed value to node's globals"""
    node.node_globals[key] = value


class Args(NamedTuple):
    """Represents args and kwargs parameters"""
    args: Iterable
    kwargs: dict


def call_args(*args_, **kwargs) -> Args:
    """Returns Args tuple from parameters"""
    return Args(args_, kwargs)


def call(node: Union[InstanceNode, Node], key: str, value: Args):
    """Calls node or node instance method"""
    target = node if hasattr(node, key) else \
             node.instance if isinstance(node, InstanceNode) else node
    getattr(target, key)(*value.args, **value.kwargs)
