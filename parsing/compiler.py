from common.reflection.activator import create
from importlib import import_module

def compile_view(node):
    return compile_node(node)

def compile_page(node, parent):
    compile_children(node, parent)

def compile_widget(node, parent):
    widget = compile_node(node, parent)
    apply_attributes(node, widget)
    apply_text(node, widget)
    compile_children(node, widget)

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
    eventName = '<' + attr[0][3:] + '>'
    handler = lambda event, command=attr[1]: run_command(command)
    widget.bind(eventName, handler)

def run_command(command):
    command = command.split(":")
    module = import_module(command[0])
    exec('module.' + command[1])

def compile_children(node, widget):
    for child in list(node):
        compile_widget(child, widget)

def compile_node(node, *args):
    # tag = "{namespace}name"
    typeDescription = node.tag.split('}')
    return create(typeDescription[0][1:], typeDescription[1], *args)
