from os.path import abspath
from pyviews.common.parsing import parse_xml
from pyviews.common import settings
from pyviews.common.compiling import CompileContext
from pyviews.compiling.core import compile_xml, setup_render, render
from pyviews.compiling.node import create_node, setup_context, use_parent_vm
from pyviews.compiling.attribute import compile_attributes, compile_text

def setup_settings():
    settings.add_compile_step(create_node)
    settings.add_compile_step(use_parent_vm)
    settings.add_compile_step(setup_context)
    settings.add_compile_step(compile_attributes)
    settings.add_compile_step(compile_text)
    settings.add_compile_step(setup_render)
    settings.add_compile_step(render)
    settings.VIEWS_FOLDER = abspath('views')

def compile_app(app_view='app'):
    xml_node = parse_xml(app_view)
    context = CompileContext(xml_node)
    return compile_xml(context)
