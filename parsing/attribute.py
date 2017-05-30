from importlib import import_module
import parsing.binding as binding
from parsing.exceptions import CommandException
from common.values import COMM_PREFIX, IMPORT_ATTR

def bind_command(node, attr):
    (name, expr) = attr
    if not binding.is_one_way_binding(expr):
        raise CommandException(name + ' value should be one way binding')
    event = name[len(COMM_PREFIX):]
    command = binding.eval_one_way(expr, node)
    node.bind(event, command)

def set_prop(node, attr):
    (name, expr) = attr
    if binding.is_two_way_binding(expr):
        apply_two_way_binding(node, attr)
    elif binding.is_one_way_binding(expr):
        apply_one_way_binding(node, attr)
    else:
        node.set_attr(name, expr)

def apply_two_way_binding(node, attr):
    (name, expr) = attr
    (var_expr, value_expr) = binding.split_two_way(expr)
    var = binding.create_var(var_expr)
    node.set_attr(name, var)
    apply_to_source_binding(node, var, value_expr)
    apply_to_view_binding(node, var, value_expr)

def apply_to_source_binding(node, var, value_expr):
    view_model = node.view_model
    update_vm = lambda *args, v=view_model, a=value_expr, content=var: setattr(v, a, content.get())
    var.trace('w', update_vm)

def apply_to_view_binding(node, var, value_expr):
    update_view = lambda new_val, old_val, content=var: content.set(new_val)
    node.view_model.observe(value_expr, update_view)
    update_view(getattr(node.view_model, value_expr), None)

def apply_one_way_binding(node, attr):
    update_view = lambda new_val, old_val, n=node, a=attr: set_node_attr(n, a)
    keys = [key for key in binding.to_dictionary(node.view_model).keys() if key in attr[1]]
    for key in keys:
        node.view_model.observe(key, update_view)
    update_view(None, None)

def set_node_attr(node, attr):
    (name, expr) = attr
    node.set_attr(name, binding.eval_one_way(expr, node))

def import_local(node, attr):
    imports = attr[1].split(',')
    for import_item in imports:
        import_to_local(node, import_item)

def import_to_local(node, import_item):
    [path, name] = import_item.split(':')
    value = import_path(path)
    node.set_context(name, value)

def import_path(path):
    try:
        return import_module(path)
    except ImportError:
        pass
    (path, name) = binding.split_by_last_dot(path)
    module = import_path(path)
    return module.__dict__[name]

def get_compile(node, attr):
    (name, expression) = attr
    for (check, apply) in APPLIES:
        if check(node, name, expression):
            return apply
    return

def hasmethod(ent, attr):
    return hasattr(ent, attr) and callable(getattr(ent, attr))

APPLIES = [
    (lambda node, name, expr: name == IMPORT_ATTR, import_local),
    (lambda node, name, expr: name.startswith(COMM_PREFIX), bind_command),
    (lambda node, name, expr: node.has_attr(name), set_prop)
]
