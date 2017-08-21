from os.path import abspath
from pyviews.common.parsing import parse_xml
from pyviews.common.compiling import CompileContext
from pyviews.common import ioc
from pyviews.common.ioc import Container, inject
from pyviews.compiling.core import compile_xml as compilexml, setup_render, render
from pyviews.compiling.node import create_node, setup_context, use_parent_vm
from pyviews.compiling.attribute import compile_attributes, compile_text
from pyviews.view.style import Style

def setup_ioc(container=None):
    ioc.CONTAINER = container or Container()

def setup_injection():
    ioc.CONTAINER.register_call('compile_xml', compilexml)
    ioc.CONTAINER.register_call('create_node', create_node)
    ioc.CONTAINER.register('compile_steps', get_compile_steps)

    ioc.CONTAINER.register_value('views_folder', abspath('views'))
    ioc.CONTAINER.register_value('event_key', 'event')
    ioc.CONTAINER.register_value('vm_key', 'vm')
    ioc.CONTAINER.register_value('node_key', 'node')
    ioc.CONTAINER.register_value('view_ext', '.xml')

def get_compile_steps(node):
    if isinstance(node, Style):
        return [render]
    return [use_parent_vm,
            setup_context,
            compile_attributes,
            compile_text,
            setup_render,
            render]

@inject('compile_xml')
def compile_app(app_view='app', compile_xml=None):
    xml_node = parse_xml(app_view)
    context = CompileContext(xml_node)
    return compile_xml(context)
