"""Module with modifiers"""
from typing import Any

from injectool import resolve

from pyviews.core import Node, import_path, InstanceNode


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


def call(node: (Node, InstanceNode), key: str, value: Any):
    """Calls node or node instance method"""
    value = _to_list(value)
    if not value or not isinstance(value[-1], dict):
        value.append({})
    args, kwargs = value[0:-1], value[-1]
    target = node if hasattr(node, key) else node.instance
    getattr(target, key)(*args, **kwargs)


def _to_list(value: Any):
    if value is None:
        return []
    if isinstance(value, tuple):
        return list(value)
    if not isinstance(value, list):
        return [value]
    return value
