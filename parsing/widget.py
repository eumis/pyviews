from common.reflection.activator import create_inst
from parsing.expressions import parse_tag, get_apply

def compile_widget(node, parent, view_model):
    widget = compile_node(node, parent)
    apply_attributes(node, widget, view_model)
    apply_text(node, widget)
    compile_children(node, widget, view_model)
    return widget

def apply_attributes(node, widget, view_model):
    for attr in node.items():
        apply_attr(widget, attr, view_model)

def apply_attr(widget, attr, view_model):
    apply = get_apply(widget, attr)
    apply(widget, attr, view_model)

def apply_property(widget, attr):
    widget.__dict__[attr[0]] = attr[1]

def apply_text(node, widget):
    text = node.text.strip()
    if text:
        widget.configure(text=text)

def compile_children(node, widget, view_model):
    children = []
    for child in list(node):
        children.append(compile_widget(child, widget, view_model))
    return children

def compile_node(node, *args):
    type_desc = parse_tag(node.tag)
    return create_inst(type_desc[0], type_desc[1], *args)
    