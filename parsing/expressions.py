from importlib import import_module
from parsing.exceptions import CommandException, InstanceException
from common.reflection.execution import run

COMM_PREFIX = 'bind-'
VIEW_MODEL_LOC = 'vm'

def parse_tag(tag):
    type_desc = tag.split('}')
    return (type_desc[0][1:], type_desc[1])

def parse_inst(expr):
    if not is_binding(expr):
        raise InstanceException('"' + expr + '" value should be instance expression')
    expr = parse_binding(expr)
    return split_by_last_dot(expr)

def get_apply(widget, attr):
    (name, expression) = attr
    for (check, apply) in APPLIES:
        if check(widget, name, expression):
            return apply
    return

def is_binding(expression):
    return expression.startswith('{') and expression.endswith('}')

def parse_binding(binding):
    return binding[1:-1]

def apply_command(widget, attr, view_model):
    (name, expr) = attr
    if not is_binding(expr):
        raise CommandException(name + ' value should be binding expression')
    expr = parse_binding(expr)
    event = '<' + name[len(COMM_PREFIX):] + '>'
    handler = lambda event_name, e=expr, vm=view_model: run_command(e, vm)
    widget.bind(event, handler)

def run_command(expression, view_model):
    (module_name, method_call) = parse_command_expression(expression)
    args = {VIEW_MODEL_LOC:view_model}
    if module_name:
        args['module'] = import_module(module_name)
        method_call = 'module.' + method_call
    run(method_call, args)

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
    (name, expression) = attr
    run('widget.' + name + "(" + expression + ")", {VIEW_MODEL_LOC:view_model, 'widget':widget})


APPLIES = [
    (lambda widget,name,expr: name.startswith(COMM_PREFIX), apply_command),
    (lambda widget,name,expr: callable(getattr(widget, name)), apply_call)
]