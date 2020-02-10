"""Module with setters"""

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


class Args:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def call(node: (Node, InstanceNode), key: str, value: Args):
    """Calls node or node instance method"""
    target = node if hasattr(node, key) else node.instance
    getattr(target, key)(*value.args, **value.kwargs)
