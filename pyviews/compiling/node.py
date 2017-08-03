from tkinter import Widget
from pyviews.common.reflection import create_inst
from pyviews.compiling.namespace import parse_namespace
from pyviews.compiling.exceptions import UnsupportedNodeException
from pyviews.view.base import CompileNode, NodeContext
from pyviews.view.core import WidgetNode

def create_node(context):
    (module_name, class_name) = parse_namespace(context.xml_node.tag)
    args = (context.parent_node.get_widget_master(),) if context.parent_node else ()
    inst = create_inst(module_name, class_name, *args)
    if isinstance(inst, Widget):
        inst = WidgetNode(inst)
    if not isinstance(inst, CompileNode):
        raise UnsupportedNodeException(type(inst).__name__)
    inst.set_xml_node(context.xml_node)
    context.node = inst

def user_parent_vm(context):
    if context.parent_node and context.parent_node.view_model:
        context.node.view_model = context.parent_node.view_model

def use_parent_context(context):
    if context.parent_node:
        context.node.context = NodeContext(context.parent_node.context)
