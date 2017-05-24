from parsing.widget import compile_widget, compile_children
from parsing.expressions import parse_attr
from common.reflection.activator import create_inst

def compile_view(node, parent, view_model=None):
    if view_model is None:
        view_model = init_view_model(node)
    if node.tag == 'view':
        return compile_children(node, parent, view_model)
    else:
        return compile_widget(node, parent, view_model)

def init_view_model(node):
    expression = node.get('view-model')
    if expression is None:
        return
    type_desc = parse_attr(expression)
    return create_inst(type_desc[0], type_desc[1])
