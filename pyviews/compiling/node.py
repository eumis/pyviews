from tkinter import Widget
from pyviews.common.reflection import create_inst
from pyviews.common.parsing import parse_namespace
from pyviews.compiling.exceptions import UnsupportedNodeException
from pyviews.view.base import CompileNode, NodeContext
from pyviews.view.core import WidgetNode

def create_node(context):
    (module_name, class_name) = parse_namespace(context.xml_node.tag)
    args = (context.master_widget,) if context.master_widget else ()
    inst = create_inst(module_name, class_name, *args)
    if isinstance(inst, Widget):
        inst = WidgetNode(inst)
    if not isinstance(inst, CompileNode):
        raise UnsupportedNodeException(type(inst).__name__)
    inst.xml_node = context.xml_node
    context.node = inst

def use_parent_vm(context):
    if context.parent_node and context.parent_node.view_model:
        context.node.view_model = context.parent_node.view_model

def setup_context(context):
    if context.parent_node:
        context.node.context = NodeContext(context.parent_node.context)
