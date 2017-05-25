from importlib import import_module
from importlib.util import find_spec as find_module
from parsing.exceptions import CommandException

COMM_PREFIX = 'bind-'

def parse_tag(expression):
    type_desc = expression.split('}')
    return (type_desc[0][1:], type_desc[1])

def parse_attr(expression):
    return expression.split(":")

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

def apply_command(widget, attr, vm):
    (name, expression) = attr
    if not is_binding(expression):
        raise CommandException(name + ' value should be binding expression')
    expression = parse_binding(expression)
    event = '<' + name[len(COMM_PREFIX):] + '>'
    handler = lambda event_name, expr=expression, vm=vm: run_command(expr, vm)
    widget.bind(event, handler)

def run_command(expression, vm):
    (module_name, method_call) = parse_command_expression(expression)
    if module_name:
        module = import_module(module_name)
        method_call = 'module.' + method_call
    exec(method_call)

def parse_command_expression(expression):
    parts = expression.split('(', maxsplit=1)
    if len(parts) == 1:
        raise CommandException('"' + expression + '" expression is not valid')
    last_dot = parts[0].rfind('.')
    if last_dot == -1:
        return('', expression)
    return (expression[:last_dot], expression[last_dot+1:])

def apply_call(widget, attr, vm):
    (name, expression) = attr
    exec('widget.' + name + "(" + expression + ")")

APPLIES = [
    (lambda widget,name,expression: name.startswith(COMM_PREFIX), apply_command),
    (lambda widget,name,expression: callable(getattr(widget, name)), apply_call)
]