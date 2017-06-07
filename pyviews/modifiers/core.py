from importlib import import_module
from pyviews.binding.expressions import split_by_last_dot

def import_global(node, attr):
    (name, path) = attr
    imported = import_path(path)
    if imported:
        node.context.globals[name] = imported

def import_path(path):
    if not path:
        return None
    try:
        return import_module(path)
    except ImportError:
        pass
    (path, name) = split_by_last_dot(path)
    module = import_path(path)
    return module.__dict__[name] if module else None

def bind(node, attr):
    (name, command) = attr
    node.bind(name, command)

def set_prop(node, attr):
    (name, value) = attr
    if not node.has_attr(name):
        return
    node.set_attr(name, value)
