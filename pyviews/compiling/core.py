from pyviews.common.settings import COMPILE_STEPS
from pyviews.compiling.context import CompileContext

def compile_node(xml_node, parent_node=None):
    context = CompileContext(xml_node, parent_node)
    for step in COMPILE_STEPS:
        step(context)
    return context.node

def compile_chidlren(context):
    context.node.render(_compile_children, context.node)

def _compile_children(node, children=None):
    compiled = []
    children = children if children else node.get_xml_children()
    for child in children:
        child = compile_node(child.xml_node, node)
        compiled.append(child)
    return compiled
