from pyviews.core.reflection import import_path
from pyviews.core.parsing import Node

def import_global(node: Node, name, path):
    imported = None
    try:
        imported = import_path(path)
    except ImportError:
        node.globals[name] = None
    node.globals[name] = imported
