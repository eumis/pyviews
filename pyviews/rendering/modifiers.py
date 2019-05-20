"""Module with modifiers"""
from typing import Any

from injectool import get_container
from pyviews.core import Node, import_path


def import_global(node: Node, key: str, path: Any):
    """Import passed module, class, function full name and stores it to node's globals"""
    node.node_globals[key] = import_path(path)


def inject_global(node: Node, global_key: str, inject_key: Any):
    """Resolves passed dependency and stores it to node's globals"""
    value = get_container().get(inject_key)
    set_global(node, global_key, value)


def set_global(node: Node, key: str, value: Any):
    """Adds passed value to node's globals"""
    node.node_globals[key] = value


def call(node: Node, key: str, value: Any):
    """Calls node or node instance method"""
    value = _to_list(value)
    if not value or not isinstance(value[-1], dict):
        value.append({})
    args = value[0:-1]
    kwargs = value[-1]
    node.__dict__[key](*args, **kwargs)


def _to_list(value: Any):
    if value is None:
        return []
    if isinstance(value, tuple):
        return list(value)
    if not isinstance(value, list):
        return [value]
    return value
