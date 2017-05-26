from parsing.widget import compile_widget
from parsing.binding import parse_inst
from common.reflection.activator import create_inst
from common.values import VM_ATTR

def compile_view(node, parent, view_model=None):
    if view_model is None:
        view_model = init_view_model(node)
    return compile_widget(node, parent, view_model)

def init_view_model(node):
    expression = node.get(VM_ATTR)
    if expression is None:
        return
    (module_name, class_name) = parse_inst(expression)
    return create_inst(module_name, class_name)
