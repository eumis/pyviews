import parsing.binding as binding
from parsing.exceptions import CommandException
from common.values import COMM_PREFIX

def bind_command(node, attr):
    (name, expr) = attr
    if not binding.is_one_way_binding(expr):
        raise CommandException(name + ' value should be one way binding')
    expr = binding.parse_one_way_binding(expr)
    event = name[len(COMM_PREFIX):]
    node.bind(event, binding.parse_command(expr))

def set_prop(node, attr):
    (name, expr) = attr
    if binding.is_two_way_binding(expr):
        apply_two_way_binding(node, attr)
    if binding.is_one_way_binding(expr):
        apply_one_way_binding(node, attr)
    node.set_attr(name, expr)

def apply_two_way_binding(node, attr):
    (name, expr) = attr
    (var_expr, value_expr) = binding.split_two_way(expr)
    var = binding.create_var(var_expr)
    node.set_attr(name, var)
    apply_to_source_binding(node, var, value_expr)
    apply_to_view_binding(node, var, value_expr)

def apply_to_source_binding(node, var, value_expr):
    update_view = lambda new_val, old_val, content=var: content.set(new_val)
    view_model = node.get_view_model()
    view_model.observe(value_expr, update_view)
    update_view(getattr(view_model, value_expr), None)

def apply_to_view_binding(node, var, value_expr):
    view_model = node.get_view_model()
    update_vm = lambda *args, v=view_model, a=value_expr, content=var: setattr(v, a, content.get())
    var.trace('w', update_vm)

def apply_one_way_binding(node, attr):
    (name, expr) = attr
    update_view = lambda new_val, old_val, n=node, a=name: n.set_attr(a, new_val)
    expr = binding.parse_one_way_binding(expr)
    view_model = node.get_view_model()
    view_model.observe(expr, update_view)
    node.set_attr(name, getattr(view_model, expr))

def get_compile(node, attr):
    (name, expression) = attr
    for (check, apply) in APPLIES:
        if check(node, name, expression):
            return apply
    return

def hasmethod(ent, attr):
    return hasattr(ent, attr) and callable(getattr(ent, attr))

APPLIES = [
    (lambda node, name, expr: name.startswith(COMM_PREFIX), bind_command),
    (lambda node, name, expr: node.has_attr(name), set_prop)
]