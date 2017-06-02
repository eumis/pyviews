from importlib import import_module
from pyviews.modifiers.core import set_prop as default_modify
from pyviews.compiling.namespace import has_namespace, parse_namespace
from pyviews.binding.vars import Variable
from pyviews.binding.expressions import split_by_last_dot, is_binding, eval_exp, to_dictionary

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

def apply_binding(node, attr, apply_changes):
    expr = attr[1]
    val = eval_exp(expr, node)
    apply_changes(val)
    if isinstance(val, Variable):
        return
    handler = lambda new, old, n=node, b=attr[1], a=apply_changes: a(eval_exp(b, n))
    keys = [key for key in to_dictionary(node.view_model).keys() if key in attr[1]]
    for key in keys:
        node.view_model.observe(key, handler)

def get_modify(namespace):
    (module, modifier) = split_by_last_dot(namespace)
    module = import_module(module)
    return getattr(module, modifier)
