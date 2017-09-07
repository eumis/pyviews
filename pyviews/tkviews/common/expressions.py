from pyviews.common.ioc import inject

def is_binding(expression):
    return expression.startswith('{') and expression.endswith('}')

@inject('run', 'node_key', 'vm_key')
def eval_exp(expression, node, run=None, node_key='node', vm_key='vm'):
    code = parse_one_way_binding(expression)
    vm_dict = {} if node.view_model is None else to_dictionary(node.view_model)
    vm_dict[vm_key] = node.view_model

    return run(code, {node_key:node, **node.context.globals, **vm_dict}, {})

def parse_one_way_binding(binding):
    return binding[1:-1]

def to_dictionary(view_model):
    return {key: getattr(view_model, key) for key in view_model.get_observable_keys()}

def split_by_last_dot(expr):
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', expr)
    return (expr[:last_dot], expr[last_dot+1:])
