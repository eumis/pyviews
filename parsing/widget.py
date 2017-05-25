from tkinter import Frame
from common.reflection.activator import create_inst
from parsing.expressions import parse_tag, get_apply
from parsing.exceptions import BindingException, UnsupportedNodeException
from view.tree import CompileNode, WidgetNode

def compile_widget(node, parent, view_model):
    widget = compile_node(node, parent)
    apply_attributes(node, widget, view_model)
    apply_text(node, widget, view_model)
    compile_children(node, widget, view_model)
    return widget

def apply_attributes(node, widget, view_model):
    for attr in node.items():
        apply_attr(widget, attr, view_model)

def apply_attr(widget, attr, view_model):
    apply = get_apply(widget, attr)
    if not apply:
        name = attr[0]
        widget_name = type(widget).__name__
        raise BindingException('There is no binding for property ' + name + ' of ' + widget_name)
    apply(widget, attr, view_model)

def apply_property(widget, attr):
    widget.__dict__[attr[0]] = attr[1]

def apply_text(node, widget, view_model):
    text = node.text.strip()
    if text:
        apply_attr(widget, ('text', text), view_model)

def compile_children(node, widget, view_model):
    children = []
    for child in list(node):
        children.append(compile_widget(child, widget, view_model))
    return children

def compile_node(node, *args):
    type_desc = parse_tag(node.tag)
    inst = create_inst(type_desc[0], type_desc[1], *args)
    if issubclass(inst, Frame):
        inst = WidgetNode(inst)
    if not issubclass(inst, CompileNode):
        raise UnsupportedNodeException(type(inst).__name__ + ' type is not supported as node')
    inst.set_node(node)
    return inst
    