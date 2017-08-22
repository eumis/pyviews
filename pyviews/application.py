from os.path import abspath
from pyviews.common import ioc
from pyviews.common.parsing import parse_xml
from pyviews.common.compiling import CompileContext
from pyviews.compiling.core import compile_xml as compilexml, setup_render, render
from pyviews.compiling.node import create_node, setup_context, use_parent_vm
from pyviews.compiling.attribute import compile_attributes, compile_text
from pyviews.compiling.styles import read_attributes, render_style, apply_style
from pyviews.view.style import Style

def setup_ioc():
    ioc.register_call('compile_xml', compilexml)
    ioc.register_call('create_node', create_node)
    ioc.register('compile_steps', get_compile_steps)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('event_key', 'event')
    ioc.register_value('vm_key', 'vm')
    ioc.register_value('node_key', 'node')
    ioc.register_value('view_ext', '.xml')

def get_compile_steps(node):
    if isinstance(node, Style):
        return [read_attributes,
                render_style]
    return [use_parent_vm,
            setup_context,
            apply_style,
            compile_attributes,
            compile_text,
            setup_render,
            render]

@ioc.inject('compile_xml')
def compile_app(app_view='app', compile_xml=None):
    xml_node = parse_xml(app_view)
    context = CompileContext(xml_node)
    return compile_xml(context)
