from importlib import import_module
from pyviews.common.parsing import has_namespace, parse_namespace
from pyviews.common.vars import Variable
from pyviews.common.expressions import split_by_last_dot, is_binding, eval_exp
from pyviews.observable.base import ViewModel

def compile_attributes(context):
    for attr in context.node.xml_node.items():
        compile_attr(context.node, attr)

def compile_text(context):
    text = context.node.xml_node.text
    text = text.strip() if text else ''
    if text:
        compile_attr(context.node, ('text', text))

def compile_attr(node, attr):
    modify = set_prop
    (name, expr) = attr
    if has_namespace(name):
        (namespace, name) = parse_namespace(name)
        modify = get_modify(namespace)
    apply = lambda value, key=name, mod=modify: mod(node, (key, value))
    try:
        if is_binding(expr):
            apply_binding(node, attr, apply)
        else:
            apply(expr)
    except Exception as ex:
        print(ex)
        print('Expression "' + expr + '" parsing is failed')

def set_prop(node, attr):
    (name, value) = attr
    node.set_attr(name, value)

def apply_binding(node, attr, apply_changes):
    expr = attr[1]
    val = eval_exp(expr, node)
    apply_changes(val)
    if isinstance(val, Variable):
        return
    if node.view_model:
        handler = lambda new, old, n=node, b=expr, a=apply_changes: a(eval_exp(b, n))
        observe_view_model(node, node.view_model, expr, handler)

def observe_view_model(node, view_model, expr, handler):
    expr_keys = [key for key in view_model.get_observable_keys() if key in expr]
    for key, value in [(key, getattr(view_model, key)) for key in expr_keys]:
        view_model.observe(key, handler)
        node.on_destroy(lambda key=key: view_model.release_callback(key, handler))
        if isinstance(value, ViewModel):
            observe_view_model(node, value, expr, handler)

def get_modify(namespace):
    (module, modifier) = split_by_last_dot(namespace)
    module = import_module(module)
    return getattr(module, modifier)
