from pyviews.common.settings import COMPILE_STEPS

def compile_xml(compile_context):
    for step in COMPILE_STEPS:
        step(compile_context)
    return compile_context.node

def setup_render(context):
    context.node.compile_xml = compile_xml

def render(context):
    context.node.render()
