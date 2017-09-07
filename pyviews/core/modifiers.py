from importlib import import_module
from pyviews.common.expressions import split_by_last_dot

def import_(node, attr):
    (name, path) = attr
    imported = _import_path(path)
    if imported is not None:
        node.context.globals[name] = imported

def _import_path(path):
    if not path:
        return None
    try:
        return import_module(path)
    except ImportError as exception:
        print(str(exception))
    (path, name) = split_by_last_dot(path)
    module = _import_path(path)
    return module.__dict__[name] if module else None
