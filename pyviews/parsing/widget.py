from tkinter import Widget
from pyviews.common.reflection.activator import create_inst
from pyviews.parsing.attribute import compile_attr
from pyviews.parsing.exceptions import UnsupportedNodeException
from pyviews.view.base import CompileNode
from pyviews.view.core import WidgetNode
from pyviews.parsing.namespace import parse_namespace

def compile_widget(xml_node, parent, view_model):
    node = compile_node(xml_node, parent, view_model)
    compile_attributes(node)
    apply_text(node)
    node.render(compile_children)
    return node

def compile_attributes(node):
    for attr in node.xml_attrs():
        compile_attr(node, attr)

def apply_text(node):
    text = node.get_text()
    if text:
        compile_attr(node, ('text', text))

def compile_children(node, children=None):
    compiled = []
    children = children if children else node.get_children()
    for child in children:
        compiled.append(compile_widget(child.xml_node, node, child.view_model))
    return compiled

def compile_node(node, parent, view_model):
    (module_name, class_name) = parse_namespace(node.tag)
    args = (parent.get_container_for_child(),) if parent else ()
    inst = create_inst(module_name, class_name, *args)
    if isinstance(inst, Widget):
        inst = WidgetNode(inst)
    if not isinstance(inst, CompileNode):
        raise UnsupportedNodeException(type(inst).__name__)
    inst.set_node(node)
    if view_model:
        inst.view_model = view_model
    if parent:
        inst.set_context(parent.get_context())
    return inst
    