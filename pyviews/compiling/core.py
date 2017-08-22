from pyviews.common.ioc import inject, get

@inject('create_node')
def compile_xml(compile_context, create_node=None):
    create_node(compile_context)
    compile_steps = get('compile_steps', compile_context.node)
    for step in compile_steps:
        step(compile_context)
    return compile_context.node

def setup_render(context):
    context.node.compile_xml = compile_xml

def render(context):
    context.node.render()
