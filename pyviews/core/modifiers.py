from pyviews.core.ioc import inject
from pyviews.core.reflection import import_path
from pyviews.core.node import Node

def import_global(node: Node, key, path):
    imported = None
    try:
        imported = import_path(path)
    except ImportError:
        node.globals[key] = None
    node.globals[key] = imported

@inject('container')
def inject_global(node: Node, global_key, inject_key, container=None):
    value = container.get(inject_key)
    set_global(node, global_key, value)

def set_global(node: Node, key, value):
    node.globals[key] = value
