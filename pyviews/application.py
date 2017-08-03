from os.path import abspath
from pyviews.common.parsing import parse_xml
from pyviews.common import settings
from pyviews.compiling.core import compile_node, compile_chidlren
from pyviews.compiling.node import create_node, use_parent_context, user_parent_vm
from pyviews.compiling.attribute import compile_attributes, compile_text

def setup_settings():
    settings.add_compile_step(create_node)
    settings.add_compile_step(user_parent_vm)
    settings.add_compile_step(use_parent_context)
    settings.add_compile_step(compile_attributes)
    settings.add_compile_step(compile_text)
    settings.add_compile_step(compile_chidlren)
    settings.VIEWS_FOLDER = abspath('views')

def compile_app(app_view='app'):
    return load_view(app_view)

def load_view(view, parent=None):
    xml_node = parse_xml(view)
    return compile_node(xml_node, parent)

def load_styles(path):
    node = load_view(path)
    return node.context.styles
