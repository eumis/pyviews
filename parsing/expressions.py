from importlib import import_module
from parsing.exceptions import CommandException, InstanceException, BindingException
from common.reflection.execution import run
from common.reflection.activator import create_inst

COMM_PREFIX = 'bind-'
VIEW_MODEL_LOC = 'vm'

def parse_tag(tag):
    type_desc = tag.split('}')
    return (type_desc[0][1:], type_desc[1])

def parse_inst(expr):
    if not is_one_way_binding(expr):
        raise InstanceException('"' + expr + '" value should be one way binding')
    expr = parse_one_way_binding(expr)
    return split_by_last_dot(expr)

def get_apply(widget, attr):
    (name, expression) = attr
    for (check, apply) in APPLIES:
        if check(widget, name, expression):
            return apply
    return

def is_one_way_binding(expression):
    return is_binding(expression) and not is_two_way_binding(expression)

def is_binding(expression):
    return expression.startswith('{') and expression.endswith('}')

def is_two_way_binding(expression):
    return expression.startswith('{{') and expression.endswith('}}')

def parse_one_way_binding(binding):
    return binding[1:-1]

def parse_two_way_binding(binding):
    return binding[2:-2]

def apply_command(widget, attr, view_model):
    (name, expr) = attr
    if not is_one_way_binding(expr):
        raise CommandException(name + ' value should be one way binding')
    expr = parse_one_way_binding(expr)
    event = '<' + name[len(COMM_PREFIX):] + '>'
    handler = lambda event_name, e=expr, vm=view_model: run_command(e, vm)
    widget.bind(event, handler)

def run_command(expression, view_model):
    (module_name, method_call) = parse_command_expression(expression)
    args = {VIEW_MODEL_LOC:view_model}
    method_container = VIEW_MODEL_LOC
    if module_name:
        args['module'] = import_module(module_name)
        method_container = 'module'
    run(method_container + '.' + method_call, args)

def parse_command_expression(expr):
    parts = expr.split('(', maxsplit=1)
    if len(parts) == 1:
        raise CommandException('"' + expr + '" expression is not valid')
    return split_by_last_dot(parts[0], expr)

def split_by_last_dot(expr, res=None):
    if res is None:
        res = expr
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', res)
    return (res[:last_dot], res[last_dot+1:])

def apply_call(widget, attr, view_model):
    (name, expr) = attr
    run('widget.' + name + "(" + expr + ")", {VIEW_MODEL_LOC:view_model, 'widget':widget})

def apply_prop(widget, attr, view_model):
    (name, expr) = attr
    set_val = lambda new_val, old_val, w=widget, a=name: setattr(w, a, new_val)
    if is_one_way_binding(expr):
        expr = parse_one_way_binding(expr)
        view_model.observe(expr, set_val)
        set_val(getattr(view_model, expr), None)
    else:
        set_val(expr, None)

def apply_config(widget, attr, view_model):
    (name, expr) = attr
    set_val = lambda new_val, old_val, w=widget, a=name: call_config(w, a, new_val)
    if is_one_way_binding(expr):
        expr = parse_one_way_binding(expr)
        view_model.observe(expr, set_val)
        set_val(getattr(view_model, expr), None)
    else:
        set_val(expr, None)

def call_config(widget, param, value):
    args = {}
    args[param] = str(value)
    widget.configure(**args)

def apply_var(widget, attr, view_model):
    (name, expr) = attr
    (var_expr, val_expr) = split_two_way(expr)
    var = create_var(var_expr)
    set_val = lambda new_val, old_val, content=var: content.set(new_val)
    view_model.observe(val_expr, set_val)
    update_vm = lambda *args, v=view_model, a=val_expr, content=var: setattr(v, a, content.get())
    var.trace('w', update_vm)
    set_val(getattr(view_model, val_expr), None)
    widget.configure(**{name:var})

def split_two_way(expr):
    parts = parse_two_way_binding(expr).split(':', maxsplit=1)
    if len(parts) == 1:
        raise BindingException(expr + ' is not valid two way binding expression')
    return tuple(parts)

def create_var(expr):
    (module_name, class_name) = split_by_last_dot(expr)
    return create_inst(module_name, class_name)

def hasmethod(ent, attr):
    return hasattr(ent, attr) and callable(getattr(ent, attr))

APPLIES = [
    (lambda widget, name, expr: name.startswith(COMM_PREFIX), apply_command),
    (lambda widget, name, expr: hasmethod(widget, name), apply_call),
    (lambda widget, name, expr: hasattr(widget, name), apply_prop),
    (lambda widget, name, expr: is_two_way_binding(expr), apply_var),
    (lambda widget, name, expr: True, apply_config)
]