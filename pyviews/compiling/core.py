from pyviews.common.ioc import inject

@inject('create_node')
def compile_xml(compile_context, create_node=None):
    create_node(compile_context)
    return run_compile_steps(compile_context)

@inject('container')
def run_compile_steps(context, container=None):
    compile_steps = container.get('compile_steps', context.node.__class__)
    for step in compile_steps:
        step(context)
    return context.node

def compile_children(context):
    context.node.compile_children()
