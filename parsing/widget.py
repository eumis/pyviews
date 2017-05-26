from tkinter import Frame, Tk, Widget
from common.reflection.activator import create_inst
from parsing.attribute import get_compile
from parsing.binding import parse_tag
from parsing.exceptions import BindingException, UnsupportedNodeException
from view.tree import CompileNode, WidgetNode, AppNode

def compile_widget(xml_node, parent, view_model):
    node = compile_node(xml_node, view_model, parent)
    compile_attributes(node)
    apply_text(node)
    node.render()
    compile_children(node)
    return node

def compile_attributes(node):
    for attr in node.xml_attrs():
        compile_attr(node, attr)

def compile_attr(node, attr):
    compile_ = get_compile(node, attr)
    # if not compile_:
    #     name = attr[0]
    #     node_name = type(node).__name__
    #     raise BindingException('There is no binding for property ' + name + ' of ' + node_name)
    if compile_:
        compile_(node, attr)

def apply_text(node):
    text = node.get_text()
    if text:
        compile_attr(node, ('text', text))

def compile_children(node):
    children = []
    parent = node.get_container_for_child()
    view_model = node.get_view_model()
    for child in node.get_xml_children():
        children.append(compile_widget(child, parent, view_model))
    return children

def compile_node(node, view_model, *args):
    (module_name, class_name) = parse_tag(node.tag)
    inst = create_inst(module_name, class_name, *args)
    if isinstance(inst, Widget):
        inst = WidgetNode(inst)
    if isinstance(inst, Tk):
        inst = AppNode(inst)
    if not isinstance(inst, CompileNode):
        raise UnsupportedNodeException(type(inst).__name__ + ' type is not supported as node')
    inst.set_node(node)
    inst.set_view_model(view_model)
    return inst
    