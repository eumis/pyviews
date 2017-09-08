from pyviews.core.reflection import import_path

def import_(node, attr):
    (name, path) = attr
    imported = import_path(path)
    if imported is not None:
        node.context.globals[name] = imported
