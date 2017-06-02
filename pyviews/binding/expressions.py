from pyviews.common.reflection.execution import run
from pyviews.common.values import VM_KEY

def is_binding(expression):
    return expression.startswith('{') and expression.endswith('}')

def eval_exp(expression, node):
    code = parse_one_way_binding(expression)
    vm_dict = to_dictionary(node.view_model)
    vm_dict[VM_KEY] = node.view_model
    return run(code, node.get_context(), vm_dict)

def to_dictionary(view_model):
    keys = [key for key in dir(view_model) if not key.startswith('_')]
    return {key: getattr(view_model, key) for key in keys}

def parse_one_way_binding(binding):
    return binding[1:-1]

def split_by_last_dot(expr, res=None):
    if res is None:
        res = expr
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', res)
    return (res[:last_dot], res[last_dot+1:])
