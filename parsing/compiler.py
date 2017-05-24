from importlib import import_module
from common.reflection.activator import create_inst
from parsing.expressions import parse_tag, parse_attr

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

def compile_widget(node, parent, vm):
    widget = compile_node(node, parent)
    apply_attributes(node, widget)
    apply_text(node, widget)
    compile_children(node, widget, vm)
    return widget

def apply_attributes(node, widget):
    for attr in node.items():
        if hasattr(widget, attr[0]):
            apply_attr(widget, attr)
        else:
            apply_command(widget, attr)

def apply_attr(widget, attr):
    item = getattr(widget, attr[0])
    if callable(item):
        apply_method(widget, attr)
    else:
        apply_property(widget, attr)

def apply_method(widget, attr):
    exec('widget.' + attr[0] + "(" + attr[1] + ")")

def apply_property(widget, attr):
    widget.__dict__[attr[0]] = attr[1]

def apply_text(node, widget):
    text = node.text.strip()
    if text:
        widget.configure(text=text)

def apply_command(widget, attr):
    if not attr[0].startswith('on-'):
        return
    event = '<' + attr[0][3:] + '>'
    handler = lambda event, command=attr[1]: run_command(command)
    widget.bind(event, handler)

def run_command(command):
    command = parse_attr(command)
    module = import_module(command[0])
    exec('module.' + command[1])

def compile_children(node, widget, vm):
    children = []
    for child in list(node):
        children.append(compile_widget(child, widget, vm))
    return children

def compile_node(node, *args):
    type_desc = parse_tag(node.tag)
    return create_inst(type_desc[0], type_desc[1], *args)
