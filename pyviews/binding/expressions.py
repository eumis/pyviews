from pyviews.common.reflection.execution import run
from pyviews.common.values import VM_KEY, NODE_KEY

def is_binding(expression):
    return expression.startswith('{') and expression.endswith('}')

def eval_exp(expression, node):
    code = parse_one_way_binding(expression)
    vm_dict = {} if node.view_model is None else to_dictionary(node.view_model)
    vm_dict[VM_KEY] = node.view_model

    return run(code, {NODE_KEY:node, **node.context.globals, **vm_dict}, {})

def to_dictionary(view_model):
    return {key: getattr(view_model, key) for key in view_model.get_observable_keys()}

def parse_one_way_binding(binding):
    return binding[1:-1]

def split_by_last_dot(expr, res=None):
    if res is None:
        res = expr
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', res)
    return (res[:last_dot], res[last_dot+1:])

def parse_dictionary(expr):
    code = '{' + expr + '}'
    return run(code, {}, {})
