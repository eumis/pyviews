from parsing.exceptions import CommandException, InstanceException, BindingException
from common.reflection.activator import create_inst
from view.actions import Command

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

def parse_command(expr):
    parts = expr.split('(', maxsplit=1)
    if len(parts) == 1:
        raise CommandException('"' + expr + '" expression is not valid')
    (caller, call) = split_by_last_dot(parts[0], expr)
    return Command(caller, call)

def split_by_last_dot(expr, res=None):
    if res is None:
        res = expr
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', res)
    return (res[:last_dot], res[last_dot+1:])

def split_two_way(expr):
    parts = parse_two_way_binding(expr).split(':', maxsplit=1)
    if len(parts) == 1:
        raise BindingException(expr + ' is not valid two way binding expression')
    return tuple(parts)

def create_var(expr):
    (module_name, class_name) = split_by_last_dot(expr)
    return create_inst(module_name, class_name)


