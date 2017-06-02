from importlib import import_module
from pyviews.modifiers.core import set_prop as default_modify
from pyviews.parsing.namespace import has_namespace, parse_namespace
from pyviews.parsing.binding import split_by_last_dot, is_binding, apply as apply_binding

def compile_attr(node, attr):
    modify = default_modify
    (name, expr) = attr
    if has_namespace(name):
        (namespace, name) = parse_namespace(name)
        modify = get_modify(namespace)
    apply = lambda value, n=node, key=name, mod=modify: mod(n, (key, value))
    if is_binding(expr):
        apply_binding(node, attr, apply)
    else:
        apply(expr)

def get_modify(namespace):
    (module, modifier) = split_by_last_dot(namespace)
    module = import_module(module)
    return getattr(module, modifier)
